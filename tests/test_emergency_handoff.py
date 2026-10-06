import json
from types import SimpleNamespace

from property_automation.maintenance_coordinator import AutomationRequest, run_property_tool_loop


class FakeMessage:
    def __init__(self, *, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        result = {"role": "assistant"}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in self.tool_calls
            ]
        return result


def tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


class ScriptedCompletions:
    def __init__(self):
        self.responses = [
            FakeMessage(
                tool_calls=[tool_call("call_1", "create_maintenance_request", {
                    "property_id": "harbor-12",
                    "tenant_id": "tenant-204",
                    "summary": "Water spreading under kitchen sink",
                    "urgency": "emergency",
                })]
            ),
            FakeMessage(
                tool_calls=[tool_call("call_2", "schedule_inspection_reminder", {
                    "maintenance_id": "mnt_0001",
                    "days_from_now": 1,
                    "note": "Inspect after the emergency repair",
                })]
            ),
            FakeMessage(content="Emergency repair recorded; inspection reminder scheduled."),
        ]

    def create(self, **kwargs):
        assert "spreading water leaks as emergency" in kwargs["messages"][0]["content"]
        assert "spreading water leaks as emergency" in kwargs["tools"][0]["function"]["description"]
        return SimpleNamespace(choices=[SimpleNamespace(message=self.responses.pop(0))])


def test_emergency_request_hands_off_to_next_day_inspection():
    result = run_property_tool_loop(
        AutomationRequest(
            property_id="harbor-12",
            tenant_id="tenant-204",
            message="Water is spreading from beneath the kitchen sink.",
            tenant_documents=["move-in-condition-report.pdf"],
        ),
        ScriptedCompletions(),
    )

    assert result.maintenance_requests[0].urgency == "emergency"
    assert len(result.inspection_reminders) == 1
    assert result.inspection_reminders[0].maintenance_id == result.maintenance_requests[0].maintenance_id
    assert result.inspection_reminders[0].note == "Inspect after the emergency repair"
