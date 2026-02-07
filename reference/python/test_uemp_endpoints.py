"""
Tests for UEMP endpoints and strict token/media enforcement.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from uemp_api import app


client = TestClient(app)


def _valid_uemp_message() -> dict:
    return {
        "meta": {
            "protocol": "uemp/1.0",
            "id": "uemp:BA:2026:ord-8f3a2e",
            "intent": "create-order",
            "conversationId": "uemp:BA:2026:conv-1234",
        },
        "data": {
            "order": {
                "id": "ORD-123",
            }
        },
        "context": {
            "note": "test-message",
        },
    }


class TestUEMPDiscovery:
    def test_well_known_uemp_exists(self):
        response = client.get("/.well-known/uemp")
        assert response.status_code == 200
        body = response.json()

        assert body["protocol"] == "uemp/1.0"
        assert body["paths"]["messages"] == "/api/uemp/messages"
        assert "application/vnd.uemp+json" in body["mediaTypes"]
        assert "/api/aip" not in json.dumps(body)

    def test_api_capabilities_exists(self):
        response = client.get("/api/uemp/capabilities")
        assert response.status_code == 200
        body = response.json()

        assert body["protocol"] == "uemp/1.0"
        assert body["paths"]["discovery"] == "/.well-known/uemp"


class TestUEMPMessageValidation:
    def test_accepts_valid_uemp_message(self):
        payload = _valid_uemp_message()
        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.uemp+json"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/vnd.uemp+json")
        assert response.headers["UEMP-Version"] == "1.0"
        assert response.headers["UEMP-Message-Id"] == payload["meta"]["id"]

        body = response.json()
        assert body["accepted"] is True
        assert body["message"]["meta"]["protocol"] == "uemp/1.0"
        assert body["validation"]["protocol"] == "ok"

    def test_rejects_non_uemp_protocol_token(self):
        payload = _valid_uemp_message()
        payload["meta"]["protocol"] = "aip/1.0"

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.uemp+json"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-invalid-version"

    def test_rejects_non_uemp_message_id(self):
        payload = _valid_uemp_message()
        payload["meta"]["id"] = "aip:BA:2026:ord-8f3a2e"

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.uemp+json"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-invalid-message-id"

    def test_rejects_non_uemp_media_type(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 415
        body = response.json()
        assert body["code"] == "protocol-unsupported-media-type"
