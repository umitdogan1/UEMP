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


def _find_legacy_aip_header(request: Request) -> str | None:
    for header_name in request.headers.keys():
        if header_name.lower().startswith("aip-"):
            return header_name
    return None


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
    if content_type.startswith("application/vnd.aip"):
        return _protocol_error(
            status_code=400,
            code="protocol-unknown-token-family",
            message=f"Token family 'aip' is not supported in media type '{content_type}'",
            hint=f"Use Content-Type: {UEMP_MEDIA_TYPE}",
            action="fix-request",
        )
    if content_type != UEMP_MEDIA_TYPE:
        return _protocol_error(
            status_code=415,
            code="protocol-unsupported-media-type",
            message=f"Unsupported media type '{content_type or 'missing'}'",
            hint=f"Use Content-Type: {UEMP_MEDIA_TYPE}",
            action="fix-request",
        )

    legacy_header = _find_legacy_aip_header(request)
    if legacy_header:
        return _protocol_error(
            status_code=400,
            code="protocol-unknown-token-family",
            message=f"Legacy header '{legacy_header}' is not supported",
            hint="Use UEMP-* headers only",
            action="fix-request",
        )

    header_version = request.headers.get("uemp-version")
    if not header_version:
        return _protocol_error(
            status_code=400,
            code="protocol-missing-required-header",
            message="Missing required header 'UEMP-Version'",
            hint="Set UEMP-Version to the envelope protocol version (e.g. 1.0)",
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
    if protocol_token.lower().startswith("aip/"):
        return _protocol_error(
            status_code=400,
            code="protocol-unknown-token-family",
            message=f"Token family 'aip' is not supported in protocol token '{protocol_token}'",
            hint="Use protocol token format uemp/X.Y",
            action="fix-message",
        )
    if not UEMP_PROTOCOL_PATTERN.fullmatch(protocol_token):
        return _protocol_error(
            status_code=400,
            code="protocol-invalid-version",
            message=f"Invalid protocol token '{protocol_token}'",
            hint="Use protocol token format uemp/X.Y",
            action="fix-message",
        )

    version = protocol_token.split("/", 1)[1]
    if header_version != version:
        return _protocol_error(
            status_code=400,
            code="protocol-header-mismatch",
            message=f"Header UEMP-Version '{header_version}' does not match meta.protocol '{protocol_token}'",
            hint=f"Set UEMP-Version to '{version}'",
            action="fix-request",
        )

    message_id = message.meta.id
    if message_id.lower().startswith("aip:"):
        return _protocol_error(
            status_code=400,
            code="protocol-unknown-token-family",
            message=f"Token family 'aip' is not supported in message ID '{message_id}'",
            hint="Use format uemp:{party}:{year}:{id}",
            action="fix-message",
        )
    if not UEMP_MESSAGE_ID_PATTERN.fullmatch(message_id):
        return _protocol_error(
            status_code=400,
            code="protocol-invalid-message-id",
            message=f"Invalid UEMP message ID '{message_id}'",
            hint="Use format uemp:{party}:{year}:{id}",
            action="fix-message",
        )

    header_message_id = request.headers.get("uemp-message-id")
    if header_message_id and header_message_id != message_id:
        return _protocol_error(
            status_code=400,
            code="protocol-header-mismatch",
            message=f"Header UEMP-Message-Id '{header_message_id}' does not match meta.id '{message_id}'",
            hint="Set UEMP-Message-Id to match meta.id or omit the header",
            action="fix-request",
        )

    header_intent = request.headers.get("uemp-intent")
    if header_intent and header_intent != message.meta.intent:
        return _protocol_error(
            status_code=400,
            code="protocol-header-mismatch",
            message=f"Header UEMP-Intent '{header_intent}' does not match meta.intent '{message.meta.intent}'",
            hint="Set UEMP-Intent to match meta.intent or omit the header",
            action="fix-request",
        )

    header_conversation_id = request.headers.get("uemp-conversation-id")
    if header_conversation_id and header_conversation_id != (
        message.meta.conversation_id or ""
    ):
        return _protocol_error(
            status_code=400,
            code="protocol-header-mismatch",
            message=(
                f"Header UEMP-Conversation-Id '{header_conversation_id}' does not match "
                f"meta.conversationId '{message.meta.conversation_id or ''}'"
            ),
            hint="Set UEMP-Conversation-Id to match meta.conversationId or omit the header",
            action="fix-request",
        )

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
