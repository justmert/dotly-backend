from fastapi.testclient import TestClient
from api.api import app
from .key import PUBLIC_KEY, BEARER_TOKEN, headers

client = TestClient(app)

import pytest


def test_account_endpoint_valid():
    response = client.get("overview/account", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "address" in response.json()
    assert "display" in response.json()


def test_account_endpoint_invalid_public_key():
    INVALID_PUBLIC_KEY = "invalid_key_here"
    response = client.get("overview/account", params={"public_key": INVALID_PUBLIC_KEY}, headers=headers)

    assert response.status_code == 404
    assert response.json().get("detail") == "Invalid public key which cannot be encoded to address"


def test_account_endpoint_no_content():
    EMPTY_PUBLIC_KEY = "empty_key_here"
    response = client.get("overview/account", params={"public_key": EMPTY_PUBLIC_KEY}, headers=headers)

    assert response.status_code == 404  # since public key is invalid


def test_balance_distribution_valid():
    response = client.get("overview/balance-distribution", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_balance_distribution_invalid_public_key():
    INVALID_PUBLIC_KEY = "invalid_key_here"
    response = client.get("overview/balance-distribution", params={"public_key": INVALID_PUBLIC_KEY}, headers=headers)

    assert response.status_code == 404
    assert response.json().get("detail") == "Invalid public key which cannot be encoded to address"


def test_identity_valid():
    response = client.get("overview/identity", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200


# 1. Test for balance-distribution
def test_balance_distribution():
    response = client.get("overview/balance-distribution", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "network" in response.json()[0]
    assert "symbol" in response.json()[0]
    assert "balance" in response.json()[0]
    assert response.json()[0]["network"] == "polkadot"


# 2. Test for identity
def test_identity():
    response = client.get("overview/identity", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "network" in response.json()[0]
    assert "display" in response.json()[0]
    assert "web" in response.json()[0]
    assert "twitter" in response.json()[0]
    assert response.json()[0]["network"] == "polkadot"


# 3. Test for balance-stats
def test_balance_stats():
    response = client.get("overview/balance-stats", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "max" in response.json()
    assert "min" in response.json()
    assert "prev24H" in response.json()


# 4. Test for balance-history
def test_balance_history():
    response = client.get("overview/balance-history", params={"public_key": PUBLIC_KEY}, headers=headers)

    if response.status_code == 200:
        assert isinstance(response.json(), list)
    else:
        assert response.status_code in [204, 404]


# Error case: Test for invalid public key
def test_invalid_public_key():
    invalid_key = "invalid_key"
    response = client.get("overview/account", params={"public_key": invalid_key}, headers=headers)

    assert response.status_code == 404


# Error case: Test for unauthorized access
def test_unauthorized_access():
    unauthorized_headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("overview/account", params={"public_key": PUBLIC_KEY}, headers=unauthorized_headers)

    assert response.status_code == 401
