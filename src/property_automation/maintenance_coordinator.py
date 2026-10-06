from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, Field


class AutomationRequest(BaseModel):
    property_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    tenant_documents: list[str] = Field(default_factory=list)


class MaintenanceRequest(BaseModel):
    maintenance_id: str
    property_id: str
    tenant_id: str
    summary: str
    urgency: str


class InspectionReminder(BaseModel):
    maintenance_id: str
    remind_on: date
    note: str


class AutomationResult(BaseModel):
    reply: str
    maintenance_requests: list[MaintenanceRequest]
    inspection_reminders: list[InspectionReminder]


@dataclass
class PropertyLedger:
    maintenance_requests: list[MaintenanceRequest] = field(default_factory=list)
    inspection_reminders: list[InspectionReminder] = field(default_factory=list)

    def create_maintenance_request(
        self, property_id: str, tenant_id: str, summary: str, urgency: str
    ) -> dict[str, str | bool]:
        maintenance_id = f"mnt_{len(self.maintenance_requests) + 1:04d}"
        request = MaintenanceRequest(
            maintenance_id=maintenance_id,
            property_id=property_id,
            tenant_id=tenant_id,
            summary=summary,
            urgency=urgency,
        )
        self.maintenance_requests.append(request)
        return {
            "maintenance_id": maintenance_id,
            "inspection_required": urgency == "emergency",
        }

    def schedule_inspection_reminder(
        self, maintenance_id: str, days_from_now: int, note: str
    ) -> dict[str, str]:
        known_ids = {request.maintenance_id for request in self.maintenance_requests}
        if maintenance_id not in known_ids:
            raise ValueError("Inspection reminder must reference a recorded maintenance request")
        reminder = InspectionReminder(
            maintenance_id=maintenance_id,
            remind_on=date.today() + timedelta(days=days_from_now),
            note=note,
        )
        self.inspection_reminders.append(reminder)
        return {"scheduled_for": reminder.remind_on.isoformat()}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_maintenance_request",
            "description": (
                "Record a tenant maintenance request. Classify active, spreading water leaks "
                "as emergency; emergency requests require an inspection."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {"type": "string"},
                    "tenant_id": {"type": "string"},
                    "summary": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["routine", "urgent", "emergency"]},
                },
                "required": ["property_id", "tenant_id", "summary", "urgency"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_inspection_reminder",
            "description": "Schedule the follow-up inspection for a recorded maintenance request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "maintenance_id": {"type": "string"},
                    "days_from_now": {"type": "integer", "minimum": 1, "maximum": 30},
                    "note": {"type": "string"},
                },
                "required": ["maintenance_id", "days_from_now", "note"],
                "additionalProperties": False,
            },
        },
    },
]


def run_property_tool_loop(
    request: AutomationRequest,
    completions: Any,
    ledger: PropertyLedger | None = None,
) -> AutomationResult:
    ledger = ledger or PropertyLedger()
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Coordinate property maintenance. Classify active, spreading water leaks "
                "as emergency. Always record the maintenance request first. "
                "If that tool reports inspection_required=true, schedule an inspection reminder "
                "for the next day. Tenant document names are context only."
            ),
        },
        {"role": "user", "content": request.model_dump_json()},
    ]
    handlers = {
        "create_maintenance_request": ledger.create_maintenance_request,
        "schedule_inspection_reminder": ledger.schedule_inspection_reminder,
    }

    for _ in range(6):
        response = completions.create(model="auto", messages=messages, tools=TOOLS)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))
        if not message.tool_calls:
            return AutomationResult(
                reply=message.content or "Request coordinated.",
                maintenance_requests=ledger.maintenance_requests,
                inspection_reminders=ledger.inspection_reminders,
            )
        for call in message.tool_calls:
            arguments = json.loads(call.function.arguments)
            output = handlers[call.function.name](**arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(output),
                }
            )
    raise RuntimeError("Tool loop reached its six-turn safety bound")
