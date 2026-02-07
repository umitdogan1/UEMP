"""
Pydantic schemas and constants for UEMP envelope handling.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


UEMP_MEDIA_TYPE = "application/vnd.uemp+json"
UEMP_VERSIONED_MEDIA_TYPE = "application/vnd.uemp.v1+json"
UEMP_PROTOCOL_PATTERN = re.compile(r"^uemp/[0-9]+\.[0-9]+$")
UEMP_MESSAGE_ID_PATTERN = re.compile(
    r"^uemp:[A-Z0-9-]{1,32}:[0-9]{4}:[a-z0-9-]{1,64}$"
)


class UEMPMeta(BaseModel):
    """UEMP envelope metadata."""

    protocol: str = Field(..., description="UEMP protocol version, e.g. uemp/1.0")
    id: str = Field(..., description="UEMP message ID")
    intent: str = Field(..., min_length=1, description="Sender intent")
    conversation_id: str | None = Field(
        default=None,
        alias="conversationId",
        description="Conversation identifier",
    )

    model_config = {"populate_by_name": True}


class UEMPMessage(BaseModel):
    """Minimal UEMP envelope shape for Phase 1 implementation."""

    meta: UEMPMeta
    data: dict[str, Any]
    context: dict[str, Any] | None = None
    signatures: list[dict[str, Any]] | None = None


class UEMPValidationResult(BaseModel):
    """Response payload for accepted UEMP messages."""

    accepted: bool = True
    message: UEMPMessage
    validation: dict[str, str]
