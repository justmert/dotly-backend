from fastapi.testclient import TestClient
from api.api import app
from .key import PUBLIC_KEY, BEARER_TOKEN, headers

client = TestClient(app)

import pytest


def test_transfer_relationship():
    response = client.get(f"stats/transfer-relationship?public_key={PUBLIC_KEY}", headers=headers)
    assert response.status_code in [200, 204, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), dict)


def test_recent_transfers():
    response = client.get(f"stats/recent-transfers?public_key={PUBLIC_KEY}", headers=headers)
    assert response.status_code in [200, 204, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), dict)


def test_transfer_history():
    for interval in ["DAY", "WEEK", "MONTH", "YEAR"]:
        response = client.get(f"stats/transfer-history?public_key={PUBLIC_KEY}&interval={interval}", headers=headers)
        assert response.status_code in [200, 204, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "xAxis" in data
            assert "yAxis" in data
            assert "series" in data


def test_total_transfers():
    response = client.get(f"stats/total-transfers?public_key={PUBLIC_KEY}", headers=headers)
    assert response.status_code in [200, 204, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), dict)


def test_transfer_relationship():
    response = client.get("stats/transfer-relationship", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "count" in response.json()
    assert "amount" in response.json()

    # Additional assertions depending on the response shape and content


def test_recent_transfers():
    response = client.get("stats/recent-transfers", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "id" in response.json()[0]
    assert "transfer" in response.json()[0]


def test_transfer_history():
    response = client.get(
        "stats/transfer-history", params={"public_key": PUBLIC_KEY, "interval": "WEEK"}, headers=headers
    )

    assert response.status_code == 200
    assert "xAxis" in response.json()
    assert "yAxis" in response.json()
    assert "series" in response.json()


def test_total_transfers():
    response = client.get("stats/total-transfers", params={"public_key": PUBLIC_KEY}, headers=headers)
    assert response.status_code == 200


def test_transfer_history_invalid_interval():
    response = client.get(
        "stats/transfer-history", params={"public_key": PUBLIC_KEY, "interval": "INVALID"}, headers=headers
    )

    assert response.status_code == 422


# Assuming no authentication token is provided
def test_unauthenticated_access():
    response = client.get("stats/transfer-relationship", params={PUBLIC_KEY: PUBLIC_KEY})
    assert response.status_code == 403
