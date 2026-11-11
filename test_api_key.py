"""Smoke test that the AmSC MAG PAT authenticates.

Uses the Responses API at the production MAG base URL:

    base_url = https://mag.genesis.americansciencecloud.org/v1
    env_key  = AMSC_TOKEN
    model    = gpt-6-luna
    wire_api = responses
    header   = X-AmSC-MAG-Provider: openai

Run:
    export AMSC_TOKEN="..."
    python test_api_key.py
    pytest test_api_key.py -v
"""

import json
import os

import pytest
import requests

BASE_URL = "https://mag.genesis.americansciencecloud.org/v1"
MODEL = "gpt-6-luna"
RESPONSES_URL = f"{BASE_URL}/responses"


@pytest.fixture
def api_key() -> str:
    key = os.environ.get("AMSC_TOKEN", "").strip()
    if not key:
        pytest.skip("Set AMSC_TOKEN to run this test")
    return key


def smoke_test(api_key: str) -> dict:
    response = requests.post(
        RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-AmSC-MAG-Provider": "openai",
        },
        json={
            "model": MODEL,
            "input": "Reply with the single word: pong",
        },
        timeout=90,
    )

    assert response.status_code not in (401, 403), (
        "API key was rejected. Check that AMSC_TOKEN is a valid MAG PAT."
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
    print("---------------- PAYLOAD ----------------")
    print(json.dumps(payload, indent=2))
    print("---------------- END PAYLOAD ----------------")
    print("---------------- OUTPUT ----------------")
    print(json.dumps(payload.get("output"), indent=2))
    print("---------------- END OUTPUT ----------------")
    print("---------------- CONTENT ----------------")
    print(json.dumps(payload.get("output")[0].get("content"), indent=2))
    print("---------------- END CONTENT ----------------")
    print("---------------- TEXT ----------------")
    print(json.dumps(payload.get("output")[0].get("content")[0].get("text"), indent=2))
    print("---------------- END TEXT ----------------")
    print("---------------- END ----------------")
    return payload


def test_api_key_works(api_key: str) -> None:
    smoke_test(api_key)


def main() -> None:
    key = os.environ.get("AMSC_TOKEN", "").strip()
    if not key:
        raise SystemExit("Set AMSC_TOKEN to run this script")
    smoke_test(key)


if __name__ == "__main__":
    main()
