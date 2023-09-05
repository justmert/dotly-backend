from fastapi.testclient import TestClient
from api.api import app
from .key import PUBLIC_KEY, BEARER_TOKEN, headers
from unittest.mock import patch

client = TestClient(app)

import pytest


def test_check_badges_successful_request():
    response = client.get(f"badges/check-badges?public_key={PUBLIC_KEY}", headers=headers)

    # Check for successful response
    assert response.status_code == 200


def test_check_badges_no_content():
    response = client.get("badges/check-badges?public_key=no_content_key", headers=headers)

    # Check for no content response
    assert response.status_code == 404


def test_check_badges_not_found():
    response = client.get("badges/check-badges?public_key=not_found_key", headers=headers)

    # Check for not found response
    assert response.status_code == 404


def test_check_badges_missing_public_key():
    response = client.get("badges/check-badges", headers=headers)

    # Check for missing public_key, FastAPI will return 422 for validation errors
    assert response.status_code == 422


def test_check_badges_with_unauthorized_user():
    # a 403 Unauthorized error will be raised by FastAPI
    response = client.get(f"badges/check-badges?public_key={PUBLIC_KEY}")

    # Check for unauthorized response
    assert response.status_code == 403
