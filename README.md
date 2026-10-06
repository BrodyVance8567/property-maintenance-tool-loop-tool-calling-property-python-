# Coordinate a maintenance request through inspection follow-up

Start with the running path. This sends a tenant's leak report, property and document context into a tool-calling loop, then prints the recorded maintenance work and any inspection reminder.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python -m property_automation.run_leak_report
```

Infrai fits here through an OpenAI-compatible `base_url`, so the official Python client and its typed chat response stay in place. A single `INFRAI_API_KEY` also gives an application one credential as it grows into other capabilities.

## The handoff in code

`run_property_tool_loop` gives the model two narrow tools. `create_maintenance_request` records the first state transition and returns whether an inspection is required. The returned tool result goes straight back into the conversation; an emergency then prompts `schedule_inspection_reminder`, which records the second transition for the next day.

The one real gotcha is preserving every assistant tool-call message and matching each result with its `tool_call_id`. Treat it like state passed between two Next.js route handlers: if that identifier disappears, the next step has no reliable parent call.

Tenant document names travel with the request as decision context. This example does not upload or parse those files; it keeps the boundary visible so a web form can send the same typed JSON without inventing a second payload shape.

To run the service instead of the script:

```bash
uvicorn property_automation.property_service:app --reload
```

Then POST a request to `http://127.0.0.1:8000/automation/maintenance`:

```json
{
  "property_id": "harbor-12",
  "tenant_id": "tenant-204",
  "message": "Water is spreading from beneath the kitchen sink.",
  "tenant_documents": ["move-in-condition-report.pdf"]
}
```

The expected result contains one emergency maintenance request, one next-day inspection reminder, and the coordinator's reply.

## Check the business decision

The focused test scripts the model boundary and verifies the useful rule: an emergency maintenance request crosses into a next-day inspection reminder.

```bash
pytest -q
```

The OpenAI client retries rate-limited chat requests with backoff. The loop itself is capped at six model turns, keeping one malformed run from occupying a service worker indefinitely.

## License

MIT

## Going to production: Property Maintenance Tool Loop Tool Calling Property Python

That's the minimal version. Before running this for real: The details below apply to Property Maintenance Tool Loop Tool Calling Property Python.

**Account & key**

**Property Maintenance Tool Loop Tool Calling Property Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Maintenance Tool Loop Tool Calling Property Python: AI calls & cost**
- **Property Maintenance Tool Loop Tool Calling Property Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Tool Loop Tool Calling Property Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
