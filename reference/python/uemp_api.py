"""
UEMP protocol endpoints (public reference implementation).

Scope:
- Strict UEMP wire token/media validation
- Message envelope validation
- Capability document endpoint
"""

from __future__ import annotations

import json

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from uemp_schemas import (
    UEMP_MEDIA_TYPE,
    UEMP_VERSIONED_MEDIA_TYPE,
    UEMP_MESSAGE_ID_PATTERN,
    UEMP_PROTOCOL_PATTERN,
    UEMPMessage,
    UEMPValidationResult,
)

router = APIRouter(prefix="/uemp", tags=["uemp"])


def _normalize_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    return content_type.split(";", 1)[0].strip().lower()


def _protocol_error(
    *,
    status_code: int,
    code: str,
    message: str,
    hint: str,
    action: str = "upgrade-client",
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "severity": "fatal",
            "message": message,
            "recovery": {
                "action": action,
                "hint": hint,
            },
        },
    )


@router.post("/messages", response_model=UEMPValidationResult)
async def ingest_uemp_message(request: Request):
    """Validate and accept a UEMP envelope."""
    content_type = _normalize_content_type(request.headers.get("content-type"))
    if content_type != UEMP_MEDIA_TYPE:
        return _protocol_error(
            status_code=415,
            code="protocol-unsupported-media-type",
            message=f"Unsupported media type '{content_type or 'missing'}'",
            hint=f"Use Content-Type: {UEMP_MEDIA_TYPE}",
            action="fix-request",
        )

    try:
        payload = await request.json()
    except (ValueError, json.JSONDecodeError):
        return _protocol_error(
            status_code=400,
            code="protocol-invalid-json",
            message="Request body is not valid JSON",
            hint="Send a valid JSON UEMP envelope",
            action="fix-request",
        )

    try:
        message = UEMPMessage.model_validate(payload)
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "code": "protocol-invalid-envelope",
                "severity": "fatal",
                "message": "Invalid UEMP envelope",
                "errors": exc.errors(),
            },
        )

    protocol_token = message.meta.protocol
    if not UEMP_PROTOCOL_PATTERN.fullmatch(protocol_token):
        return _protocol_error(
            status_code=400,
            code="protocol-invalid-version",
            message=f"Invalid protocol token '{protocol_token}'",
            hint="Use protocol token format uemp/X.Y",
            action="fix-message",
        )

    message_id = message.meta.id
    if not UEMP_MESSAGE_ID_PATTERN.fullmatch(message_id):
        return _protocol_error(
            status_code=400,
            code="protocol-invalid-message-id",
            message=f"Invalid UEMP message ID '{message_id}'",
            hint="Use format uemp:{party}:{year}:{id}",
            action="fix-message",
        )

    version = protocol_token.split("/", 1)[1]
    response = UEMPValidationResult(
        accepted=True,
        message=message,
        validation={"protocol": "ok", "id": "ok"},
    )
    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
        headers={
            "UEMP-Version": version,
            "UEMP-Message-Id": message_id,
        },
        media_type=UEMP_MEDIA_TYPE,
    )


@router.get("/capabilities")
async def get_uemp_capabilities():
    """Return API-local UEMP capabilities."""
    return {
        "protocol": "uemp/1.0",
        "mediaTypes": [UEMP_MEDIA_TYPE, UEMP_VERSIONED_MEDIA_TYPE],
        "paths": {
            "messages": "/api/uemp/messages",
            "discovery": "/.well-known/uemp",
        },
        "headers": {
            "required": ["UEMP-Version"],
            "supported": [
                "UEMP-Version",
                "UEMP-Message-Id",
                "UEMP-Intent",
                "UEMP-Conversation-Id",
            ],
        },
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title="UEMP Reference API",
        version="0.1.0",
        description="Public reference implementation for UEMP envelope validation",
    )
    api = APIRouter(prefix="/api")
    api.include_router(router)
    app.include_router(api)

    @app.get("/.well-known/uemp")
    async def well_known_uemp():
        return {
            "protocol": "uemp/1.0",
            "mediaTypes": [UEMP_MEDIA_TYPE, UEMP_VERSIONED_MEDIA_TYPE],
            "paths": {
                "messages": "/api/uemp/messages",
                "capabilities": "/api/uemp/capabilities",
                "discovery": "/.well-known/uemp",
            },
            "headers": {
                "required": ["UEMP-Version"],
                "supported": [
                    "UEMP-Version",
                    "UEMP-Message-Id",
                    "UEMP-Intent",
                    "UEMP-Conversation-Id",
                ],
            },
        }

    return app


app = create_app()
