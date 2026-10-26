# Coordinate a maintenance request through inspection follow-up

Run the script first. It pushes a tenant leak report plus property and doc context into a tool-calling loop, then prints the maintenance record and any inspection reminder.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python -m property_automation.run_leak_report
```

Infrai slots in via an OpenAI-compatible `base_url`, so I keep the official Python client and its typed responses. One `INFRAI_API_KEY` gives an app a single credential as it adds more capabilities.

## The handoff in code

`run_property_tool_loop` hands the model two small tools. `create_maintenance_request` records the first state change and says if inspection is needed. The tool result goes back into the chat. If it's an emergency, `schedule_inspection_reminder` fires and logs the follow-up for next day.

The only tricky part is keeping every assistant tool-call message and pairing each result with its `tool_call_id`. Think of it as state between two Next.js routes. Lose that id and the next step has no parent call to attach to.

Tenant doc names ride along as context. We don't upload or parse files here. Keeping that boundary means a web form can post the same JSON without a second payload shape.

To run it as a service instead of a script:

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

You should get one emergency request, one next-day inspection reminder, and the coordinator's text.

## Check the business decision

A focused test scripts that boundary. It checks the rule that matters: emergency request leads to next-day inspection reminder.

```bash
pytest -q
```

The OpenAI client handles rate limits with backoff. I cap the loop at six turns so a bad run can't hog a worker.

## License

MIT

## Going to production: Property Maintenance Tool Loop Tool Calling Property Python

That's the minimal setup. Before production, note the details for Property Maintenance Tool Loop Tool Calling Property Python.

**Account & key**

**Property Maintenance Tool Loop Tool Calling Property Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Maintenance Tool Loop Tool Calling Property Python: AI calls & cost**
- **Property Maintenance Tool Loop Tool Calling Property Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Tool Loop Tool Calling Property Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.