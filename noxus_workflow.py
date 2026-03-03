import requests
from config import BASE_URL, API_KEY, WORKFLOW_ID, INPUT_NAME

def trigger_workflow(location: str) -> str | None:
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {"input": {INPUT_NAME: location}}
    run_url = f"{BASE_URL.rstrip('/')}/v1/workflows/{WORKFLOW_ID}/runs"

    r = requests.post(run_url, json=payload, headers=headers, verify=False)
    r.raise_for_status()

    data = r.json()
    return data.get("id")