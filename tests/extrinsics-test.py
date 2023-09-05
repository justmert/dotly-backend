from fastapi.testclient import TestClient
from api.api import app
from .key import PUBLIC_KEY, BEARER_TOKEN, headers
from unittest.mock import patch

client = TestClient(app)

import pytest

# Sample test data and endpoint
endpoint = "extrinsics/activity"
sample_public_key = PUBLIC_KEY
valid_interval = "DAY"


def test_total_extrinsics():
    response = client.get("extrinsics/total-extrinsics", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "total_count" in response.json()


def test_activity_valid_input():
    response = client.get(f"{endpoint}?public_key={sample_public_key}&interval={valid_interval}", headers=headers)
    assert response.status_code == 200
    assert "title" in response.json()
    assert "xAxis" in response.json()
    assert "yAxis" in response.json()
    assert "series" in response.json()


def test_activity_missing_data():
    response = client.get(f"{endpoint}?public_key=missing_key&interval={valid_interval}", headers=headers)
    assert response.status_code == 204


def test_activity_invalid_interval():
    invalid_interval = "decade"
    response = client.get(f"{endpoint}?public_key={sample_public_key}&interval={invalid_interval}", headers=headers)
    assert response.status_code == 422  # since it is invalid


def test_activity_missing_interval():
    response = client.get(f"{endpoint}?public_key={sample_public_key}", headers=headers)
    assert response.status_code == 422


def test_activity_missing_public_key():
    response = client.get(f"{endpoint}?interval={valid_interval}", headers=headers)
    assert response.status_code == 422


def test_extrinsics_distribution_successful_request():
    response = client.get(f"extrinsics/distribution?public_key={sample_public_key}&interval=DAY", headers=headers)

    # Check for successful response
    assert response.status_code == 200

    # Basic structure checks (you can add more specific validations if needed)
    assert "calls" in response.json()
    assert "pallets" in response.json()


def test_extrinsics_distribution_missing_public_key():
    response = client.get(f"extrinsics/distribution?interval=DAY", headers=headers)

    assert response.status_code == 422
