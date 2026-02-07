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


def _uemp_headers(**overrides: str) -> dict[str, str]:
    headers = {
        "Content-Type": "application/vnd.uemp+json",
        "UEMP-Version": "1.0",
    }
    headers.update(overrides)
    return headers


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
            headers=_uemp_headers(),
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
            headers=_uemp_headers(),
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-unknown-token-family"

    def test_rejects_non_uemp_message_id(self):
        payload = _valid_uemp_message()
        payload["meta"]["id"] = "aip:BA:2026:ord-8f3a2e"

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers=_uemp_headers(),
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-unknown-token-family"

    def test_rejects_legacy_aip_media_type(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.aip+json", "UEMP-Version": "1.0"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-unknown-token-family"

    def test_rejects_non_uemp_media_type(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 415
        body = response.json()
        assert body["code"] == "protocol-unsupported-media-type"

    def test_accepts_application_json_fallback_media_type(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json", "UEMP-Version": "1.0"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/vnd.uemp+json")

    def test_accepts_versioned_uemp_media_type(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.uemp.v1+json", "UEMP-Version": "1.0"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/vnd.uemp+json")

    def test_rejects_missing_uemp_version_header(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers={"Content-Type": "application/vnd.uemp+json"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-missing-required-header"

    def test_rejects_mismatched_uemp_version_header(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers=_uemp_headers(**{"UEMP-Version": "2.0"}),
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-header-mismatch"

    def test_rejects_legacy_aip_headers(self):
        payload = _valid_uemp_message()

        response = client.post(
            "/api/uemp/messages",
            data=json.dumps(payload),
            headers=_uemp_headers(**{"AIP-Version": "1.0"}),
        )

        assert response.status_code == 400
        body = response.json()
        assert body["code"] == "protocol-unknown-token-family"
