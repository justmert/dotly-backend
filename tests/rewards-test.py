from fastapi.testclient import TestClient
from api.api import app
from .key import PUBLIC_KEY, BEARER_TOKEN, headers

client = TestClient(app)

import pytest


def test_total_rewards():
    response = client.get("rewards/total-rewards", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "total_amount" in response.json()
    assert "total_count" in response.json()


def test_recent_rewards():
    response = client.get("rewards/recent-rewards", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for reward in response.json():
        assert "amount" in reward
        assert "id" in reward
        assert "timestamp" in reward
        assert "validatorId" in reward
        assert "era" in reward


def test_reward_history():
    response = client.get(
        "rewards/reward-history", params={"public_key": PUBLIC_KEY, "interval": "DAY"}, headers=headers
    )

    assert response.status_code == 200
    assert "title" in response.json()
    assert "xAxis" in response.json()
    assert "yAxis" in response.json()
    assert "series" in response.json()


def test_reward_relationship():
    response = client.get("rewards/reward-relationship", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 200
    assert "count" in response.json()
    assert "amount" in response.json()


def test_total_rewards_missing_public_key():
    response = client.get("rewards/total-rewards", headers=headers)

    # 422 Unprocessable Entity is typical for validation errors in FastAPI
    assert response.status_code == 422


def test_total_rewards_nonexistent_public_key():
    response = client.get("rewards/total-rewards", params={"public_key": "nonexistent_key"}, headers=headers)

    assert response.status_code == 204


def test_recent_rewards_missing_public_key():
    response = client.get("rewards/recent-rewards", headers=headers)

    assert response.status_code == 422


def test_recent_rewards_nonexistent_public_key():
    response = client.get("rewards/recent-rewards", params={"public_key": "nonexistent_key"}, headers=headers)

    assert response.status_code == 204


def test_reward_history_invalid_interval():
    response = client.get(
        "rewards/reward-history", params={"public_key": PUBLIC_KEY, "interval": "INVALID_INTERVAL"}, headers=headers
    )

    # 422 Unprocessable Entity is typical for validation errors in FastAPI
    assert response.status_code == 422


def test_reward_history_missing_interval():
    response = client.get("rewards/reward-history", params={"public_key": PUBLIC_KEY}, headers=headers)

    assert response.status_code == 422


def test_reward_relationship_missing_public_key():
    response = client.get("rewards/reward-relationship", headers=headers)

    assert response.status_code == 422


def test_reward_relationship_nonexistent_public_key():
    response = client.get("rewards/reward-relationship", params={"public_key": "nonexistent_key"}, headers=headers)

    assert response.status_code == 204


def test_unauthorized_access():
    response = client.get("rewards/total-rewards", params={"public_key": PUBLIC_KEY})

    assert response.status_code == 403  # 403 Unauthorized
