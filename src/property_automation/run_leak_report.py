from .maintenance_coordinator import AutomationRequest, run_property_tool_loop
from .property_service import build_ai_client


def main() -> None:
    request = AutomationRequest(
        property_id="harbor-12",
        tenant_id="tenant-204",
        message="Water is spreading from beneath the kitchen sink.",
        tenant_documents=["move-in-condition-report.pdf"],
    )
    client = build_ai_client()
    result = run_property_tool_loop(request, client.chat.completions)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
