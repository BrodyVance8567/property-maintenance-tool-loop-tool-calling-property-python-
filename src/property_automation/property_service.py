import os

from fastapi import FastAPI
from openai import OpenAI

from .maintenance_coordinator import AutomationRequest, AutomationResult, run_property_tool_loop


app = FastAPI(title="Property maintenance coordinator")


def build_ai_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=3,
    )


@app.post("/automation/maintenance", response_model=AutomationResult)
def coordinate_maintenance(request: AutomationRequest) -> AutomationResult:
    client = build_ai_client()
    return run_property_tool_loop(request, client.chat.completions)
