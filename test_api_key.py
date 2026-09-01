"""Smoke test that the AMSC I2 API key authenticates.

Uses the Responses API at the AMSC base URL from the Codex provider config:

    base_url = https://api.i2-core.american-science-cloud.org/v1
    env_key  = AMSC_I2_API_KEY
    model    = gpt-5.4-mini
    wire_api = responses

Run:
    export AMSC_I2_API_KEY="..."
    pytest test_api_key.py -v
"""

import os

import pytest
import requests

BASE_URL = "https://api.i2-core.american-science-cloud.org/v1"
MODEL = "gpt-5.4-mini"
RESPONSES_URL = f"{BASE_URL}/responses"


@pytest.fixture
def api_key() -> str:
    key = os.environ.get("AMSC_I2_API_KEY", "").strip()
    if not key:
        pytest.skip("Set AMSC_I2_API_KEY to run this test")
    return key


def test_api_key_works(api_key: str) -> None:
    response = requests.post(
        RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "input": "Reply with the single word: pong",
            "reasoning": {"effort": "medium"},
        },
        timeout=90,
    )

    assert response.status_code not in (401, 403), (
        "API key was rejected. Check that AMSC_I2_API_KEY is valid."
    )
    assert response.status_code == 200, (
        f"Unexpected status {response.status_code}: {response.text}"
    )

    payload = response.json()
    error = payload.get("error")
    assert not error, f"API returned an error: {error}"
    assert payload.get("object") == "response" or "output" in payload, (
        f"Unexpected response shape: {payload!r}"
    )
