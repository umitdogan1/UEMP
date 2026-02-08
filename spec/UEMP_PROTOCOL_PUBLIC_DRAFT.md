# UEMP — Unified Enterprise Messaging Protocol

## A Universal AI-Native Protocol for Enterprise Business Messaging

**Version**: 0.1.0 (Public Draft)
**Status**: Public Draft
**Last Updated**: 2026-02-07

**Naming Transition Notice**: This draft is UEMP-only. Legacy `AIP` wire tokens MUST be rejected. No backward compatibility is provided.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem](#2-the-problem)
3. [Why Now — The Consumer Has Changed](#3-why-now--the-consumer-has-changed)
4. [Design Principles](#4-design-principles)
5. [Protocol Architecture](#5-protocol-architecture)
   - [5.1 Media Type](#51-media-type)
   - [5.2 Transport Bindings](#52-transport-bindings)
   - [5.3 Capability Discovery](#53-capability-discovery)
6. [Message Structure](#6-message-structure)
7. [Format Specification](#7-format-specification)
8. [Problem Solutions](#8-problem-solutions)
   - [A. Security](#a-security)
   - [B. Data Integrity](#b-data-integrity)
   - [C. Workflow & State](#c-workflow--state)
   - [D. Scale](#d-scale)
   - [E. Evolution](#e-evolution)
   - [F. Compliance](#f-compliance)
   - [G. Internationalization](#g-internationalization)
   - [H. AI-Specific](#h-ai-specific)
9. [Schema Registry](#9-schema-registry)
   - [9.4 Conformance Classes](#94-conformance-classes)
   - [9.5 Validation Pipeline](#95-validation-pipeline)
   - [9.6 Protocol Profiles & Universal Coverage Framework](#96-protocol-profiles--universal-coverage-framework)
10. [Protocol Comparison](#10-protocol-comparison)
11. [Strengths & Weaknesses](#11-strengths--weaknesses)
12. [Open Problems](#12-open-problems)
13. [Adoption Notes](#13-adoption-notes)
14. [Specific Concerns Deep-Dive](#14-specific-concerns-deep-dive)
    - [14.1 JAdES Digital Signatures](#141-jades-digital-signatures)
    - [14.2 Determinism](#142-determinism)
    - [14.3 Legal Standing](#143-legal-standing)
    - [14.4 Lossless Round-Trip Fidelity](#144-lossless-round-trip-fidelity)
    - [14.5 AI Hallucination in Critical Messages](#145-ai-hallucination-in-critical-messages)
    - [14.6 Security Attack Surface](#146-security-attack-surface)
    - [14.7 Performance Analysis](#147-performance-analysis)
    - [14.8 Governance & Standards Politics](#148-governance--standards-politics)

---

## 1. Executive Summary

UEMP (Unified Enterprise Messaging Protocol) is a proposed universal message format designed for AI as the primary consumer of enterprise business messages. Instead of formats designed decades ago for human programmers to parse (EDIFACT, NDC XML, UBL, ISO 20022), UEMP provides a single JSON-based format that any AI system can understand natively — with self-describing semantics, embedded validation rules, and lossless round-trip conversion to native protocols.

**Core thesis**: The consumer of enterprise messages is changing from human programmers to AI. When the consumer changes, the format should change too.

**"Lossless" in UEMP context**: UEMP guarantees *semantic* lossless conversion — all business meaning is preserved. *Structural* fidelity (XML element ordering, whitespace) is preserved via native mappings. *Byte-level* equivalence is explicitly not a goal. See [Section 14.4](#144-lossless-round-trip-fidelity) for the complete three-level fidelity definition.

**What UEMP is NOT**:
- Not a transport protocol (uses HTTP, AMQP, or any transport)
- Not a replacement for TLS/mTLS (handles application-layer security only)
- Not an API specification (it's a message format, transport-agnostic)

---

## 2. The Problem

Every enterprise protocol carries the same fundamental limitation: **it was designed for human programmers to implement**.

| Protocol | Created | For | Format | Pain Point |
|----------|---------|-----|--------|------------|
| **EDIFACT** | 1987 | EDI systems with kilobytes of RAM | Segment-based (`NAD+BY+5412345000176::9`) | Cryptic, requires extensive documentation to parse |
| **IATA NDC** | 2012 | Java/C# XML parsers | XML with namespaces | Verbose, namespace-heavy, deep nesting, version sprawl (15.2→24.3) |
| **PEPPOL BIS / UBL** | 2006 | B2B document exchange | XML with multiple namespace prefixes | Extremely verbose, multiple overlapping standards |
| **ISO 20022** | 2004 | Financial messaging systems | XML (replacing SWIFT MT) | Hundreds of message types, very deep nesting |
| **HL7 FHIR** | 2014 | Healthcare systems | JSON/XML | Closest to AI-friendly, but still heavy structural overhead |
| **FIX** | 1992 | Trading systems | Tag=value pairs (`35=D\|49=SENDER\|`) | Performance-optimized but cryptic |
| **XBRL** | 2000 | Financial reporting | XML | Extremely complex taxonomy system |
| **GS1 / EANCOM** | 1990s | Retail supply chain | EDIFACT-based | Legacy segment format, slow evolution |

**The integration tax**: Every company connecting to each protocol builds custom parsers, validators, transformers, and test suites. This costs billions globally and is repeated for every new integration, every version upgrade, every protocol addition.

**The AI tax**: Teaching AI each protocol means loading thousands of tokens of specification context per message. An EDIFACT message is 50 tokens, but understanding it requires 2,000+ tokens of documentation. This is repeated for every AI interaction.

---

## 3. Why Now — The Consumer Has Changed

```
1970s-2000s: Human programmers read specs → write parsers → maintain code
2020s+:      AI reads the message → understands it → acts on it
```

Historical precedent for format evolution when the consumer changes:

| Era | Consumer Changed From→To | Format Changed From→To |
|-----|--------------------------|----------------------|
| 1960s | Punch cards → Terminals | Batch jobs → Interactive commands |
| 1980s | Terminals → GUIs | Text commands → Visual interfaces |
| 2000s | Humans → Machines | HTML pages → REST APIs |
| **2020s** | **Human programmers → AI** | **Protocol-specific XML/EDI → AI-native format** |

Previous attempts at universal enterprise messaging (ebXML, OAGIS, UN/CEFACT Core Component Library) failed because:
- They required **human programmers** to learn yet another complex spec
- The mapping effort was equal to the original integration effort
- There was no AI to bridge semantic gaps
- The "universal" format was just another rigid schema

**UEMP is different because AI changes the adoption dynamic**:
- AI doesn't "learn" a new format — it reads a schema in its context window
- AI handles ambiguity and semantic nuance that rigid code cannot
- AI can maintain cross-protocol mappings that would be impractical to hand-code
- The cost of supporting a new format is dramatically lower with AI

---

## 4. Design Principles

1. **Intent + Data** — Messages carry both structured data AND what the sender wants to happen
2. **Self-Describing** — AI should understand any message without loading external specs
3. **Token-Optimized** — Minimize total AI comprehension cost (message + context needed)
4. **Lossless Provenance** — Always traceable back to native protocol for compliance
5. **JSON Carrier** — Every language parses it, every AI model understands it natively
6. **Flat Over Deep** — Minimize nesting depth, maximize readability
7. **Works Without AI** — Traditional systems can process the structured `data` section
8. **Preserve Unknown** — Unknown fields are preserved, never stripped (forward compatibility)

---

## 5. Protocol Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UEMP Message                                  │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐ │
│  │    meta      │  │    data      │  │  context    │  │ signatures│ │
│  │             │  │              │  │             │  │           │ │
│  │ WHO/WHAT    │  │ THE business │  │ WHY/HOW     │  │ PROOF     │ │
│  │ intent      │  │ content      │  │ AI layer    │  │ integrity │ │
│  │ routing     │  │              │  │ semantics   │  │           │ │
│  │ provenance  │  │ processable  │  │ provenance  │  │ immutable │ │
│  │ Core        │  │ by anyone    │  │ Runtime     │  │           │ │
│  │ SIGNED ─────┼──┼── SIGNED ───┼──┼─ UNSIGNED ──┼──┼───────────┤ │
│  └─────────────┘  └──────────────┘  └────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

**Key architectural decision**: Only `meta` + `data` are signed (payload profile). The `context` section is mutable — AI can enrich, annotate, and add mappings without breaking signatures. This separates the legally binding content from the AI interpretation layer. Provenance uses a dual-layer model: `meta.provenanceCore` (signed, immutable origin events) and `context.provenanceRuntime` (mutable intermediary events). See [Section F1](#f1-audit-trail--provenance-chain).

### 5.1 Media Type

UEMP messages use the media type:

```
application/vnd.uemp+json
```

This will be registered with IANA per [RFC 6838](https://tools.ietf.org/html/rfc6838). Until registration is complete, implementations SHOULD use this type and MUST accept `application/json` as a fallback.

Versioned media type (for content negotiation):
```
application/vnd.uemp.v1+json
```

### 5.2 Transport Bindings

UEMP is transport-agnostic. This section defines bindings for common transports.

#### 5.2.1 HTTP Binding

**Request headers**:
```http
POST /uemp HTTP/1.1
Content-Type: application/vnd.uemp+json
Accept: application/vnd.uemp+json
UEMP-Version: 1.0
UEMP-Intent: create-order
UEMP-Conversation-Id: uemp:BA:2024:conv-1234
UEMP-Idempotency-Key: AG-2024-order-8f3a-v1
```

**Response headers**:
```http
HTTP/1.1 200 OK
Content-Type: application/vnd.uemp+json
UEMP-Version: 1.0
UEMP-Message-Id: uemp:BA:2024:ord-8f3a2e
UEMP-Conversation-Id: uemp:BA:2024:conv-1234
```

**HTTP status code mapping**:

| HTTP Status | UEMP Meaning |
|------------|-------------|
| `200 OK` | Synchronous success (response body is UEMP message) |
| `202 Accepted` | Async processing started (body has tracking info) |
| `400 Bad Request` | UEMP validation error (body is UEMP error message) |
| `404 Not Found` | Unknown conversation/message ID |
| `409 Conflict` | Idempotency key reuse with different payload |
| `413 Payload Too Large` | Message exceeds 1 MB limit |
| `415 Unsupported Media Type` | Not `application/vnd.uemp+json` or `application/json` |
| `422 Unprocessable Entity` | Valid UEMP but business rule failure (body is UEMP error) |
| `429 Too Many Requests` | Rate limited (include `Retry-After` header) |
| `500 Internal Server Error` | Processing error (body is UEMP error if possible) |

**SSE streaming** (for AI enrichment and long-running operations):
```http
GET /uemp/stream?conversationId=uemp:BA:2024:conv-1234
Accept: text/event-stream
UEMP-Version: 1.0
```

```
event: uemp-message
data: {"meta":{"intent":"ack-processing"},"data":{"status":"validating"}}

event: uemp-message
data: {"meta":{"intent":"ack-processing"},"data":{"status":"enriching"}}

event: uemp-message
data: {"meta":{"intent":"order-confirmed"},"data":{"orderId":"BA-ORD-2024-5678"}}

event: done
data: {"conversationId":"uemp:BA:2024:conv-1234","messageCount":3}
```

#### 5.2.2 AMQP Binding

For message broker / event-driven architectures:

| AMQP Property | UEMP Mapping |
|--------------|-------------|
| `content_type` | `application/vnd.uemp+json` |
| `message_id` | `meta.id` |
| `correlation_id` | `meta.conversationId` |
| `reply_to` | Response queue name |
| `type` | `meta.intent` |
| `headers.uemp-version` | `meta.protocol` version number |

**Routing key convention**: `uemp.{domain}.{intent}` (e.g., `uemp.air-travel.create-order`).

#### 5.2.3 WebSocket Binding

For bidirectional real-time communication:

```
Frame format: Each WebSocket text frame contains exactly one UEMP JSON message.
```

Connection handshake:
```
GET /uemp/ws HTTP/1.1
Upgrade: websocket
Sec-WebSocket-Protocol: uemp.v1
```

The server MUST respond with `Sec-WebSocket-Protocol: uemp.v1` to confirm UEMP support.

### 5.3 Capability Discovery

**Problem**: How does a sender know if a receiver supports UEMP, which version, and which domains?

**Solution**: A well-known endpoint for capability discovery:

```http
GET /.well-known/uemp HTTP/1.1
Accept: application/json
```

Response:
```json
{
  "uemp": {
    "versions": ["1.0"],
    "domains": ["air-travel", "invoicing", "payment"],
    "intents": {
      "air-travel": ["create-order", "cancel-order", "shop", "price", "ticket"],
      "invoicing": ["create-invoice", "credit-note"],
      "payment": ["authorize", "capture", "refund"]
    },
    "capabilities": {
      "signatures": true,
      "encryption": true,
      "streaming": true,
      "batch": true,
      "maxMessageSize": "1MB",
      "maxBatchSize": 50000
    },
    "endpoints": {
      "sync": "https://api.example.com/uemp",
      "stream": "https://api.example.com/uemp/stream",
      "websocket": "wss://api.example.com/uemp/ws",
      "batch": "https://api.example.com/uemp/batch"
    },
    "nativeProtocols": ["IATA-NDC/21.3", "IATA-NDC/24.3", "PEPPOL-BIS/3.0"]
  }
}
```

This allows:
- **Content negotiation**: Sender knows which UEMP version and domains to use
- **Protocol bridge discovery**: Sender sees which native protocols the receiver can accept alongside UEMP
- **Capability adaptation**: Sender adjusts behavior (e.g., skip encryption if not supported)
- **Automated integration**: AI agents can discover and connect to UEMP-enabled services without manual configuration

---

## 6. Message Structure

### 6.1 Complete Example

Business scenario: **Round-trip flight booking for 1 adult, London to New York, with payment and invoicing** — a transaction that today requires NDC + ISO 20022 + PEPPOL (three separate protocol implementations).

```json
{
  "meta": {
    "protocol": "uemp/1.0",
    "id": "uemp:BA:2024:ord-8f3a2e",
    "timestamp": "2024-03-15T08:30:00Z",
    "intent": "create-order",
    "domains": ["air-travel", "payment", "invoicing"],
    "source": {
      "party": { "id": "AGENCY-12345", "role": "travel-agency" },
      "native": [
        { "protocol": "IATA-NDC", "version": "21.3", "message": "OrderCreateRQ" }
      ]
    },
    "target": {
      "party": { "id": "BA", "role": "airline" }
    },
    "replyTo": "uemp:BA:2024:shop-7b2c1d",
    "ttl": "2024-03-15T09:30:00Z",
    "environment": "production",
    "idempotencyKey": "AG-2024-order-8f3a-v1",
    "ackRequested": ["received", "business"]
  },

  "data": {
    "travelers": [
      {
        "ref": "pax-1",
        "category": "adult",
        "name": { "given": "John", "surname": "Smith" },
        "birthDate": "1985-03-15",
        "gender": "male",
        "contact": {
          "email": "john.smith@email.com",
          "phone": "+44-7700-900123"
        },
        "documents": [
          {
            "type": "passport",
            "number": "P12345678",
            "issuingCountry": "GB",
            "nationality": "GB",
            "expiry": "2029-06-15"
          }
        ]
      }
    ],

    "journeys": [
      {
        "ref": "j-1",
        "direction": "outbound",
        "segments": [
          {
            "ref": "seg-1",
            "from": { "code": "LHR", "terminal": "5" },
            "to": { "code": "JFK", "terminal": "7" },
            "departure": "2024-03-15T09:00+00:00",
            "arrival": "2024-03-15T14:00-05:00",
            "carrier": "BA",
            "flight": "117",
            "cabin": "economy",
            "bookingClass": "Y",
            "aircraft": "777-300ER"
          }
        ]
      },
      {
        "ref": "j-2",
        "direction": "inbound",
        "segments": [
          {
            "ref": "seg-2",
            "from": { "code": "JFK", "terminal": "7" },
            "to": { "code": "LHR", "terminal": "5" },
            "departure": "2024-03-22T11:00-05:00",
            "arrival": "2024-03-22T22:00+00:00",
            "carrier": "BA",
            "flight": "118",
            "cabin": "economy",
            "bookingClass": "Y",
            "aircraft": "777-300ER"
          }
        ]
      }
    ],

    "pricing": {
      "total": { "amount": "1250.00", "currency": "GBP" },
      "breakdown": [
        { "type": "base-fare", "amount": "980.00", "currency": "GBP", "per": "pax-1" },
        { "type": "tax", "code": "GB", "amount": "182.00", "currency": "GBP" },
        { "type": "surcharge", "code": "YQ", "amount": "88.00", "currency": "GBP" }
      ]
    },

    "payment": {
      "method": "card",
      "card": {
        "type": "visa",
        "maskedNumber": "****4242",
        "holder": "JOHN SMITH",
        "expiry": "2026-12"
      },
      "amount": { "amount": "1250.00", "currency": "GBP" }
    },

    "offer": {
      "shoppingRef": "uemp:BA:2024:shop-7b2c1d",
      "offerId": "OF789",
      "items": ["OI001", "OI002"],
      "expiry": "2024-03-15T09:30:00Z"
    }
  },

  "context": {
    "summary": "Round-trip economy booking, 1 adult, LHR-JFK on BA, departing Mar 15 returning Mar 22, total GBP 1250",

    "constraints": [
      { "rule": "future-date", "fields": ["journeys[*].segments[*].departure"], "description": "All departures must be future dates" },
      { "rule": "age-category", "fields": ["travelers[*]"], "description": "Traveler birth date must match category (adult=12+)" },
      { "rule": "offer-valid", "fields": ["offer.expiry"], "description": "Offer must not be expired at time of booking" },
      { "rule": "payment-matches-total", "fields": ["payment.amount", "pricing.total"], "description": "Payment amount must equal pricing total" }
    ],

    "nativeMapping": {
      "IATA-NDC/21.3": {
        "travelers[0].category=adult": "Passenger/PTC=ADT",
        "journeys[0].segments[0].cabin=economy": "CabinType/Code=M",
        "journeys[0].segments[0].bookingClass=Y": "RBD=Y",
        "pricing.breakdown[1].code=GB": "Tax/TaxCode=GB",
        "pricing.breakdown[2].code=YQ": "FeeDetail/FeeCode=YQ"
      },
      "EDIFACT/D97B": {
        "travelers[0].category=adult": "QTY+PAX:1:ADT",
        "journeys[0].segments[0]": "TVL+240315:0900+240315:1400+LHR+JFK+BA+117:B+Y"
      },
      "PEPPOL-BIS/3.0": {
        "pricing.total": "LegalMonetaryTotal/PayableAmount=1250.00 GBP",
        "pricing.breakdown[1]": "TaxTotal/TaxSubtotal/TaxableAmount"
      }
    },

    "timezones": {
      "LHR": "Europe/London",
      "JFK": "America/New_York"
    },

    "processingHints": {
      "urgency": "standard",
      "idempotent": true,
      "retryable": true
    }
  },

  "signatures": [
    {
      "id": "sig-sender",
      "party": { "id": "AGENCY-12345", "role": "sender" },
      "scope": ["meta", "data"],
      "algorithm": "RS256",
      "certificate": "https://pki.agency.com/cert/2024.pem",
      "timestamp": {
        "authority": "https://tsa.example.com",
        "value": "2024-03-15T08:30:00Z",
        "token": "MIIHzwYJKoZIhvc..."
      },
      "value": "eyJhbGciOiJSUzI1NiJ9.eyJtZXRhIjp7Li..."
    }
  ]
}
```

### 6.2 Same Business Event in Current Protocols

**EDIFACT** (~200 bytes, cryptic — PNR addition for the same booking):
```
UNH+1+PNRADD:11:1:IA+ABC123'
ORG+:1A+LHR'
TVL+240315:0900+240315:1400+LHR+JFK+BA+117:B+Y'
TVL+240322:1100+240322:1400+JFK+LHR+BA+118:B+Y'
TIF+SMITH:A+JOHN:B'
SSR+DOCS+HK+1+++P+GBR+P12345678+GBR+850315+M+SMITH+JOHN'
```

> Note: EDIFACT uses a different message type (PNRADD) for the same business operation because its message taxonomy differs from NDC. The business content — traveler, flights, documents — is equivalent.

**NDC XML** (~3,000 bytes, verbose):
```xml
<OrderCreateRQ xmlns="http://www.iata.org/IATA/2015/00/2021.3/IATA_OrderCreateRQ"
  Version="21.3">
  <Document>
    <Name>NDC OrderCreateRQ</Name>
    <ReferenceVersion>21.3</ReferenceVersion>
  </Document>
  <Party>
    <Sender>
      <TravelAgencySender>
        <AgencyID>12345678</AgencyID>
        <IATA_Number>12345678</IATA_Number>
      </TravelAgencySender>
    </Sender>
  </Party>
  <Query>
    <Passengers>
      <Passenger PassengerID="PAX1">
        <PTC>ADT</PTC>
        <Individual>
          <Surname>SMITH</Surname>
          <GivenName>JOHN</GivenName>
          <Birthdate>1985-03-15</Birthdate>
          <Gender>Male</Gender>
        </Individual>
      </Passenger>
    </Passengers>
    <!-- ... 60+ more lines ... -->
  </Query>
</OrderCreateRQ>
```

**UEMP** (~700 bytes compact, self-describing):
```json
{
  "meta": { "intent": "create-order", "source": { "native": [{ "protocol": "IATA-NDC", "version": "21.3" }] } },
  "data": {
    "travelers": [{ "category": "adult", "name": { "given": "John", "surname": "Smith" } }],
    "journeys": [
      { "direction": "outbound", "segments": [
        { "from": "LHR", "to": "JFK", "departure": "2024-03-15T09:00+00:00", "carrier": "BA", "flight": "117", "cabin": "economy" }
      ]},
      { "direction": "inbound", "segments": [
        { "from": "JFK", "to": "LHR", "departure": "2024-03-22T11:00-05:00", "carrier": "BA", "flight": "118", "cabin": "economy" }
      ]}
    ]
  },
  "context": { "summary": "Round-trip London-NYC, 1 adult, BA economy" }
}
```

### 6.3 Token Efficiency Comparison

| Protocol | Message Tokens | Context Tokens Needed | Total AI Cost |
|----------|---------------|----------------------|---------------|
| EDIFACT | ~50 | ~2,000 (spec docs) | **~2,050** |
| NDC XML | ~800 | ~1,000 (schema context) | **~1,800** |
| UBL XML | ~1,000 | ~1,000 (schema context) | **~2,000** |
| **UEMP** | ~200 | ~0 (self-describing) | **~200** |

**~10x more efficient per message** for AI processing. Note: context token costs amortize when processing many messages of the same protocol in a session. The advantage is largest for single-message or low-volume interactions, which is the dominant pattern in enterprise messaging.

---

## 7. Format Specification

### 7.1 Field Naming Conventions

| Rule | Example | Rationale |
|------|---------|-----------|
| Full English words | `departure` not `dpt` or `DTM+189` | AI reads instantly, no lookup |
| camelCase | `birthDate`, `bookingClass` | JSON convention, universal |
| Domain-neutral where possible | `travelers` not `passengers` | Works for air, rail, hotel |
| Qualified when ambiguous | `pricing.total` vs `offer.expiry` | No confusion about which total |
| No abbreviations | `issuingCountry` not `issCtry` | Except universally known: `id`, `url`, `ref` |

### 7.2 The `ref` System

Internal cross-references use simple string IDs:

```json
{ "ref": "pax-1", "category": "adult", "name": { "..." : "..." } }
```
```json
{ "type": "base-fare", "per": "pax-1" }
```

No XPath. No ID/IDREF schema complexity. Just strings.

### 7.3 Message Identifiers

Message IDs follow a canonical format:

```
uemp:{party}:{year}:{type}-{unique}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `uemp` | Protocol prefix (fixed) | `uemp` |
| `{party}` | Issuing party identifier | `BA`, `AG`, `PEPPOL` |
| `{year}` | Year of creation (4-digit) | `2024` |
| `{type}-{unique}` | Message type + unique ID | `ord-8f3a2e`, `msg-0004` |

Examples:
- `uemp:BA:2024:ord-8f3a2e` — an order from BA
- `uemp:AG:2024:msg-0003` — a message from the agency
- `uemp:BA:2024:conv-1234` — a conversation identifier

**Canonical format** (ABNF):

```abnf
message-id    = "uemp:" party-id ":" year ":" local-id
party-id      = 1*32(UPPER / DIGIT / "-")
year          = 4DIGIT
local-id      = 1*64(LOWER / DIGIT / "-")

UPPER         = %x41-5A   ; A-Z
LOWER         = %x61-7A   ; a-z
DIGIT         = %x30-39   ; 0-9
```

**Regex**: `^uemp:[A-Z0-9-]{1,32}:[0-9]{4}:[a-z0-9-]{1,64}$`

Rules:
- Colons (`:`) are **structural separators only** — they delimit the four segments. Colons MUST NOT appear inside `party-id` or `local-id` segments.
- `party-id`: uppercase alphanumeric + hyphens (`[A-Z0-9-]`), 1-32 characters
- `local-id`: lowercase alphanumeric + hyphens (`[a-z0-9-]`), 1-64 characters
- Maximum total length: 128 characters
- `local-id` MUST be unique within the issuing party's namespace for the given year

### 7.4 Amounts — Always Explicit

**Every amount carries its currency. Always. No exceptions.**

**Amounts are strings, not numbers.** JSON numbers are IEEE 754 floating-point, where `0.1 + 0.2 != 0.3`. Every serious financial protocol (ISO 20022, SWIFT, PEPPOL) uses string representation for monetary values to avoid precision loss.

```json
{ "amount": "1250.00", "currency": "GBP" }
```

Rules:
- Amount values MUST be strings with explicit decimal places (e.g., `"1250.00"`, not `1250` or `1250.0`)
- No implicit currency inherited from document level — redundant but bug-proof
- Decimal separator is always `.` (period), never `,` (comma)
- No thousands separator
- Precision is determined by the currency (e.g., 2 decimal places for GBP/USD, 0 for JPY, 3 for BHD)

### 7.5 Codes — Human-Readable in `data`, Native in `context`

In `data`:
```json
"cabin": "economy"
```

In `context.nativeMapping`:
```json
"cabin=economy": "CabinType/Code=M"
```

AI understands `"economy"` immediately. Native code `M` preserved for round-trip conversion.

### 7.6 Reserved Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `$enc` | Encrypted field | `{ "$enc": "eyJ...", "$kid": "key-id" }` |
| `$link` | External reference | `{ "$link": "https://...", "$checksum": "sha256:..." }` |
| `$inline` | Inline binary data | `{ "$inline": "base64", "$value": "/9j/4AA..." }` |
| `$pending` | Known-missing field | `{ "$pending": "required before ticketing" }` |
| `ext` | Extension namespace | `{ "ext": { "agency-crm": { "..." : "..." } } }` |

> **Note**: `$link` is used instead of `$ref` to avoid collision with JSON Schema's `$ref` keyword (which is used for schema composition). If UEMP messages are validated with JSON Schema processors, `$ref` would be dereferenced as a schema reference rather than treated as data.

---

## 8. Problem Solutions

> This section provides solutions for each problem category. For deep-dive analysis of the hardest problems (signatures, determinism, legal standing, hallucination, security, performance), see [Section 14](#14-specific-concerns-deep-dive).

### A. Security

#### A1. Digital Signatures

**Problem**: XML has XML-DSIG + C14N (mature, legally proven). JSON lacks equivalent legal standing. See [Section 14.1](#141-jades-digital-signatures) for the JAdES deep-dive.

**Solution**: JWS (RFC 7515) + JCS (RFC 8785) canonicalization.

```json
{
  "signatures": [
    {
      "id": "sig-sender",
      "party": { "id": "AGENCY-12345", "role": "sender" },
      "scope": ["meta", "data"],
      "algorithm": "RS256",
      "certificate": "https://pki.agency.com/cert/2024.pem",
      "timestamp": {
        "authority": "https://tsa.example.com",
        "value": "2024-03-15T08:30:00Z",
        "token": "MIIHzwYJKoZIhvc..."
      },
      "value": "eyJhbGciOiJSUzI1NiJ9..."
    }
  ]
}
```

Design decisions:
- By default, the **payload profile** signs only `meta` + `data` — `context` is mutable (AI can enrich without breaking the sender's signature)
- The **transport profile** MAY additionally include `context` in scope (gateway attests the enrichment state at transit time)
- Multiple signatures supported (sender signs, gateway countersigns, receiver acks)
- Timestamp authority proves WHEN it was signed (non-repudiation)
- JWS is battle-tested (every JWT on the internet uses it)

**Signature profiles**:

| Profile | Purpose | Required Scope | Who Signs | Additional Fields |
|---------|---------|---------------|-----------|-------------------|
| **payload** | Legal business signature by the message sender | `["meta", "data"]` only — MUST NOT include `context` | Message sender (originator) | `id`, `party`, `scope`, `algorithm`, `certificate`, `value` |
| **transport** | Integrity attestation by an intermediary | `["meta", "data"]` minimum — MAY include `"context"` | Gateway / intermediary | All payload fields + `previousSignature` (chain link) |
| **jades** | eIDAS-qualified electronic signature (ETSI TS 119 182) | `["meta", "data"]` only — same as payload | Qualified trust service provider | All payload fields + `profile: "JAdES-B-LTA"`, `signingCertificate`, `signingTime` |

Profile rules:
- `payload` profile: `scope` MUST be exactly `["meta", "data"]`. Including `context` would bind mutable data to the sender's signature, preventing intermediary enrichment.
- `transport` profile: `scope` MUST include at least `["meta", "data"]` and MAY include `"context"` to attest the enrichment state at the moment of transit.
- `jades` profile: extends `payload` with ETSI TS 119 182 fields. `algorithm` MUST be PS256 or stronger (per ETSI requirements).

**Multi-signature disambiguation**: When a message has multiple signatures, each must be identifiable:

```json
{
  "signatures": [
    {
      "id": "sig-sender",
      "party": { "id": "AGENCY-12345", "role": "sender" },
      "scope": ["meta", "data"],
      "algorithm": "RS256",
      "certificate": "https://pki.agency.com/cert/2024.pem",
      "timestamp": { "authority": "https://tsa.example.com", "value": "2024-03-15T08:30:00Z" },
      "value": "eyJhbGciOiJSUzI1NiJ9..."
    },
    {
      "id": "sig-gateway",
      "party": { "id": "UEMP-GW-001", "role": "gateway" },
      "scope": ["meta", "data", "context"],
      "algorithm": "RS256",
      "certificate": "https://pki.gateway.com/cert/2024.pem",
      "timestamp": { "authority": "https://tsa.example.com", "value": "2024-03-15T08:30:02Z" },
      "previousSignature": "sig-sender",
      "value": "eyJhbGciOiJSUzI1NiJ9..."
    }
  ]
}
```

Signature rules:
- Each signature MUST have a unique `id` and identify the signing `party`
- `scope` declares which message sections are covered
- `previousSignature` creates a chain — the gateway signature covers the sender's signature (counter-signing)
- Verification order: validate signatures in reverse chronological order (latest first)
- Conflict resolution: if two signatures cover overlapping scope, the most recent takes precedence for `context`; for `meta` and `data`, all covering signatures must agree (mismatch = integrity error)

**Remaining gap**: Legal equivalence with XML-DSIG in jurisdictions that specifically mandate it (EU eIDAS). This requires regulatory work, not technical work.

#### A2. Field-Level Encryption

**Problem**: Sensitive fields (card numbers, passport numbers) need encryption beyond TLS.

**Solution**: JWE (RFC 7516) per-field encryption.

```json
{
  "payment": {
    "card": {
      "type": "visa",
      "holder": "JOHN SMITH",
      "number": {
        "$enc": "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00ifQ...",
        "$kid": "ba-payment-key-2024"
      }
    }
  }
}
```

Rules:
- `$enc` marker identifies encrypted fields
- `$kid` identifies which decryption key to use
- Unencrypted fields remain readable (AI processes message partially)
- Signing happens AFTER encryption (sign what you send)

#### A3. Confidentiality Classification

**Problem**: Different fields need different protection levels in storage, logging, and processing.

```json
{
  "meta": {
    "classification": {
      "default": "internal",
      "fields": {
        "travelers[*].documents": "confidential",
        "travelers[*].contact.email": "restricted",
        "payment.card": "secret"
      }
    }
  }
}
```

| Level | Log? | Cache? | AI Training? | Share with 3rd Party? |
|-------|------|--------|-------------|----------------------|
| `public` | Yes | Yes | Yes | Yes |
| `internal` | Yes | Yes | With consent | No |
| `restricted` | Masked only | Encrypted | No | No |
| `confidential` | No | Encrypted | No | No |
| `secret` | No | No (process in-memory only) | No | No |

> **Design decision**: Classification lives in `meta` (signed) rather than `context` (mutable) because classification determines how the message is stored, cached, and logged — these decisions must be tamper-proof and set by the sender, not modifiable by intermediaries.

---

### B. Data Integrity

#### B1. Canonicalization

**Problem**: JSON has no standard serialization. `{"a":1,"b":2}` and `{"b":2,"a":1}` are byte-different.

**Solution**: RFC 8785 (JCS) is mandatory for signing:
- Keys sorted lexicographically
- Numbers in shortest form (no trailing zeros)
- Strings with minimal escaping
- No whitespace between tokens
- UTF-8 encoding

Libraries exist for JavaScript, Python, Java, Go, Rust, C#.

For human readability (non-signing contexts): pretty-print with 2-space indentation is recommended. Processors must accept both.

#### B2. Null vs Missing vs Empty

**Problem**: Three states that mean different things. Critical for lossless round-tripping.

| State | JSON | Meaning | NDC XML Equivalent |
|-------|------|---------|-------------------|
| **Missing** | key absent | No information provided | Element omitted |
| **Null** | `"field": null` | Explicitly no value | `<Field xsi:nil="true"/>` |
| **Empty** | `"field": ""` | Value exists but empty | `<Field></Field>` |
| **Present** | `"field": "value"` | Value provided | `<Field>value</Field>` |

#### B3. Character Encoding & Internationalization

**Solution**: JSON mandates UTF-8. Names in any script, with optional Latin transliteration:

```json
{
  "name": {
    "given": "太郎",
    "surname": "山田",
    "latin": { "given": "Taro", "surname": "Yamada" }
  }
}
```

The `latin` subfield supports IATA Timatic requirements for ticketing.

#### B4. Time Zones & Date Handling

**Rules**:
- Absolute timestamps (message sent, offer expiry): **UTC with `Z` suffix**
- Local times (departure, arrival): **with UTC offset**
- Timezone identifiers: **in `context` for display**

```json
{
  "data": {
    "segments": [{
      "departure": "2024-03-15T09:00+00:00",
      "arrival": "2024-03-15T14:00-05:00"
    }]
  },
  "meta": { "timestamp": "2024-03-15T08:30:00Z" },
  "context": {
    "timezones": { "LHR": "Europe/London", "JFK": "America/New_York" }
  }
}
```

Unambiguous. AI calculates flight duration correctly (10 hours).

---

### C. Workflow & State

#### C1. Message Correlation & Conversations

**Problem**: Enterprise transactions are multi-message conversations (NDC booking = 5-8 messages).

```json
{
  "meta": {
    "id": "uemp:BA:2024:msg-0004",
    "conversationId": "uemp:BA:2024:conv-1234",
    "replyTo": "uemp:AG:2024:msg-0003",
    "sequence": 4,
    "causedBy": ["uemp:AG:2024:msg-0001", "uemp:AG:2024:msg-0003"]
  }
}
```

| Field | Purpose |
|-------|---------|
| `id` | Unique message identifier |
| `conversationId` | Groups all messages in one business flow |
| `replyTo` | Direct response to which message |
| `sequence` | Order within conversation |
| `causedBy` | Which earlier messages led to this one (DAG) |

#### C2. Workflow State Machines

**Problem**: What are the valid next steps in a business flow?

```json
{
  "meta": {
    "workflow": {
      "stateModel": "air-travel/booking-flow/v2",
      "current": "order-created",
      "validTransitions": [
        { "action": "pay", "target": "payment-completed" },
        { "action": "cancel", "target": "order-cancelled" },
        { "action": "modify", "target": "order-modified", "conditions": ["before-departure"] }
      ],
      "history": [
        { "state": "offer-selected", "at": "2024-03-15T08:25:00Z" },
        { "state": "order-created", "at": "2024-03-15T08:30:00Z" }
      ]
    }
  }
}
```

State model definition (in schema registry):
```json
{
  "stateModel": "air-travel/booking-flow/v2",
  "states": {
    "shopping": { "transitions": ["offer-selected", "abandoned"] },
    "offer-selected": { "transitions": ["order-created", "abandoned"] },
    "order-created": { "transitions": ["payment-completed", "order-cancelled", "order-modified"] },
    "payment-completed": { "transitions": ["ticketed", "refund-requested"] },
    "ticketed": { "transitions": ["checked-in", "refund-requested", "exchanged"] },
    "order-cancelled": { "terminal": true },
    "abandoned": { "terminal": true }
  }
}
```

#### C3. Error Responses

**Problem**: Current protocols have cryptic errors (`<Error Code="911" ShortText="Unable to process"/>`).

```json
{
  "meta": {
    "intent": "error",
    "replyTo": "uemp:AG:2024:msg-0003"
  },
  "data": {
    "errors": [
      {
        "code": "offer-expired",
        "severity": "fatal",
        "field": "offer.expiry",
        "expected": "future timestamp",
        "actual": "2024-03-15T09:30:00Z (expired 15 minutes ago)",
        "message": "The selected offer has expired",
        "recovery": null
      },
      {
        "code": "document-incomplete",
        "severity": "recoverable",
        "field": "travelers[0].documents",
        "expected": "at least one valid travel document",
        "actual": "no documents provided",
        "message": "Passport or national ID required for LHR-JFK route",
        "recovery": {
          "action": "provide-document",
          "requiredFields": ["type", "number", "issuingCountry", "expiry"],
          "hint": "International travel between GB and US requires valid passport"
        }
      }
    ]
  },
  "context": {
    "summary": "Order failed: 1 fatal (expired offer), 1 recoverable (missing passport)"
  }
}
```

Key differences from current protocol errors:
- **`field` pointer** — AI knows exactly which field caused the error
- **`expected` vs `actual`** — AI understands the gap
- **`severity`** — `fatal` (stop) vs `recoverable` (fix and retry)
- **`recovery`** — specific instructions for resolution
- **Natural language summary** — AI relays directly to user

**Error Code Registry**:

Error codes follow the format `{category}-{specific}` using kebab-case. Categories:

| Category | Prefix | Description |
|----------|--------|-------------|
| **Protocol** | `protocol-*` | UEMP envelope/format errors |
| **Validation** | `validation-*` | Schema and data validation errors |
| **Business** | `business-*` | Business logic rule violations |
| **System** | `system-*` | Infrastructure/processing errors |

**Standard error codes** (built-in — all implementations MUST support these):

| Code | Severity | Description |
|------|----------|-------------|
| `protocol-invalid-version` | fatal | Unsupported UEMP protocol version |
| `protocol-malformed` | fatal | Message does not parse as valid JSON |
| `protocol-missing-meta` | fatal | Missing required `meta` section |
| `protocol-missing-data` | fatal | Missing required `data` section |
| `protocol-unknown-intent` | fatal | Unrecognized `meta.intent` value |
| `protocol-message-too-large` | fatal | Message exceeds 1 MB size limit |
| `protocol-field-too-large` | fatal | Single field exceeds 64 KB limit |
| `protocol-signature-invalid` | fatal | Signature verification failed (tampered or wrong key) |
| `protocol-signature-expired` | fatal | Signing certificate has expired |
| `protocol-pagination-conflict` | recoverable | Request contains both `requestCursor` and `currentPage` (mutual exclusion) |
| `validation-schema-failed` | fatal | Message fails JSON Schema validation |
| `validation-required-field` | recoverable | Required field is missing |
| `validation-invalid-type` | recoverable | Field value has wrong type |
| `validation-invalid-format` | recoverable | Field value has wrong format (date, email, etc.) |
| `validation-invalid-code` | recoverable | Value not in codelist |
| `validation-constraint-failed` | recoverable | Business constraint check failed |
| `business-offer-expired` | fatal | Referenced offer has expired |
| `business-duplicate-request` | fatal | Idempotency key already processed (different payload) |
| `business-state-invalid` | fatal | Workflow state does not allow this action |
| `business-insufficient-data` | recoverable | Message needs additional fields to proceed |
| `business-amount-mismatch` | recoverable | Payment/pricing amounts don't agree |
| `system-internal-error` | fatal | Unexpected processing error |
| `system-service-unavailable` | fatal | Backend service temporarily unavailable |
| `system-rate-limited` | fatal | Too many requests; retry after `retryAfter` |
| `system-timeout` | fatal | Processing exceeded time limit |

**Domain-specific codes**: Domains MAY define additional codes following the format `{domain}-{specific}` (e.g., `air-travel-flight-not-found`, `invoicing-tax-rate-invalid`). Domain-specific codes are registered in the schema registry under `domains/{domain}/errors.json`.

**Error response structure**:
```json
{
  "code": "validation-required-field",
  "severity": "fatal | recoverable | warning",
  "field": "JSONPath pointer to the field (e.g., travelers[0].documents)",
  "expected": "what was expected",
  "actual": "what was found (or null if missing)",
  "message": "human-readable description",
  "recovery": {
    "action": "suggested fix action",
    "requiredFields": ["fields needed to fix"],
    "hint": "AI-friendly suggestion",
    "retryAfter": "ISO 8601 duration (for rate-limiting only)"
  }
}
```

#### C4. Idempotency

```json
{
  "meta": {
    "idempotencyKey": "AG-2024-order-8f3a-attempt-1"
  }
}
```

Same key = same result, no duplicate processing. Receiver stores key→result mapping for 24 hours (configurable).

#### C5. Three-Level Acknowledgments

**Level 1**: Technical receipt (immediate, <1 second):
```json
{
  "meta": { "intent": "ack-received", "replyTo": "..." },
  "data": { "receivedAt": "2024-03-15T08:30:01Z" }
}
```

**Level 2**: Processing status (async, seconds-minutes):
```json
{
  "meta": { "intent": "ack-processing", "replyTo": "..." },
  "data": {
    "status": "validating",
    "estimatedCompletion": "2024-03-15T08:30:30Z",
    "trackingUrl": "https://api.ba.com/status/msg-0003"
  }
}
```

**Level 3**: Business response (async, seconds-hours):
```json
{
  "meta": { "intent": "order-confirmed", "replyTo": "..." },
  "data": { "orderId": "BA-ORD-2024-5678" }
}
```

Sender configures which levels they want:
```json
{ "meta": { "ackRequested": ["received", "processing", "business"] } }
```

---

### D. Scale

#### D1. Streaming & Batch

**Batch mode** — NDJSON (Newline Delimited JSON):
```
{"meta":{"batch":{"id":"b-001","index":0,"total":50000},"intent":"create-invoice"},"data":{...}}
{"meta":{"batch":{"id":"b-001","index":1,"total":50000},"intent":"create-invoice"},"data":{...}}
```

Properties:
- Each line: complete UEMP message, independently parseable
- Streamable: process line-by-line, no need to buffer entire batch
- Resumable: restart from any line on failure
- Compressible: gzipped NDJSON

**Streaming mode** — Server-Sent Events:
```
event: uemp-message
data: {"meta":{"intent":"price-update","stream":true},"data":{"flight":"BA117","price":{"amount":"450.00","currency":"GBP"}}}
```

**Batch envelope** (optional):
```json
{
  "meta": {
    "intent": "batch",
    "batch": {
      "id": "b-001",
      "messageCount": 50000,
      "domain": "invoicing",
      "checksum": "sha256:abc123..."
    }
  }
}
```

#### D2. Large Messages & Size Limits

- Recommended max single message: **1 MB**
- If exceeding: use `$link` external references

```json
{
  "data": {
    "lineItems": {
      "$link": "https://storage.company.com/invoices/inv-001/items.ndjson",
      "$type": "external-collection",
      "$count": 10000,
      "$checksum": "sha256:def456..."
    }
  }
}
```

#### D3. Binary Attachments

Attachments live inside the `data` section (part of the signed business payload). Two content modes:

```json
{
  "data": {
    "attachments": [
      {
        "ref": "att-1",
        "name": "invoice.pdf",
        "type": "application/pdf",
        "size": 245780,
        "checksum": "sha256:9f86d08...",
        "content": { "$link": "https://storage.company.com/docs/invoice.pdf" }
      },
      {
        "ref": "att-2",
        "name": "receipt.jpg",
        "type": "image/jpeg",
        "size": 48200,
        "content": { "$inline": "base64", "$value": "/9j/4AAQSkZJRg..." }
      }
    ]
  }
}
```

- **`$link`**: external URL (recommended for >50KB)
- **`$inline`**: base64 in-message (small files only)
- Both carry checksum for integrity

#### D4. Pagination & Cursors

**Problem**: Responses with large result sets (search results, invoice line items, booking lists) need pagination to avoid oversized messages.

**Solution**: Cursor-based pagination in `meta`. Request and response use distinct field shapes:

**Response shape** (server → client):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `totalItems` | integer | OPTIONAL | Total number of items in the full result set. Servers MAY omit if count is expensive. |
| `pageSize` | integer | REQUIRED | Number of items in the current page |
| `currentPage` | integer | OPTIONAL | 1-based page index. Included for informational purposes only. |
| `totalPages` | integer | OPTIONAL | Total number of pages. MUST be present if `totalItems` is present. |
| `cursor.next` | string or null | REQUIRED | Opaque cursor for the next page. `null` on the final page. |
| `cursor.previous` | string or null | REQUIRED | Opaque cursor for the previous page. `null` on the first page. |

```json
{
  "meta": {
    "intent": "search-results",
    "pagination": {
      "totalItems": 2847,
      "pageSize": 50,
      "currentPage": 1,
      "totalPages": 57,
      "cursor": {
        "next": "eyJvZmZzZXQiOjUwfQ==",
        "previous": null
      }
    }
  },
  "data": {
    "results": [ "... 50 items ..." ]
  }
}
```

**Request shape** (client → server):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requestCursor` | string | CONDITIONAL | Opaque cursor string from a previous response's `cursor.next` or `cursor.previous`. MUST NOT be present if `currentPage` is present. |
| `currentPage` | integer | CONDITIONAL | 1-based page index for offset-based access. MUST NOT be present if `requestCursor` is present. |
| `pageSize` | integer | OPTIONAL | Requested page size (default: 50, max: 1,000) |

```json
{
  "meta": {
    "intent": "search-results",
    "replyTo": "uemp:SRV:2024:msg-0010",
    "pagination": {
      "requestCursor": "eyJvZmZzZXQiOjUwfQ==",
      "pageSize": 50
    }
  }
}
```

**Mutual exclusion constraint**: A request MUST NOT contain both `requestCursor` and `currentPage`. If both are present, the server MUST reject with error code `protocol-pagination-conflict`.

Rules:
- Cursors are opaque strings — consumers MUST NOT parse or construct them
- `cursor.next` is `null` on the final page
- `cursor.previous` is `null` on the first page
- Default page size: 50 items; maximum: 1,000 items
- For very large collections (>10,000 items), use batch mode (NDJSON) instead of pagination
- First-page requests MAY omit both `requestCursor` and `currentPage` (server returns page 1)

#### D5. Field and Value Size Limits

| Constraint | Limit | Rationale |
|-----------|-------|-----------|
| Max single message size | 1 MB | Fits in typical HTTP body limits |
| Max string field value | 64 KB | Prevents abuse; covers most text fields |
| Max array items (inline) | 10,000 | Beyond this, use `$link` or batch mode |
| Max object nesting depth | 20 levels | Prevents stack overflow in parsers |
| Max field name length | 128 characters | Reasonable for `camelCase` names |
| Max `$inline` binary size | 256 KB | Beyond this, use `$link` |
| Max message ID length | 128 characters | See [Section 7.3](#73-message-identifiers) |

Processors MUST reject messages exceeding these limits with error code `protocol-message-too-large` or `protocol-field-too-large` (see [Section C3](#c3-error-responses)).

---

### E. Evolution

#### E1. Two-Track Versioning

```json
{
  "meta": {
    "protocol": "uemp/1.2",
    "domains": ["air-travel/3.0", "payment/1.1"]
  }
}
```

| Track | What | How Often |
|-------|------|-----------|
| Protocol version (`uemp/X.Y`) | Envelope structure (meta/data/context) | Rarely |
| Domain version (`domain/X.Y`) | Business field definitions | Per domain release |

#### E2. Compatibility Rules

| Change Type | Version Impact | Example |
|------------|---------------|---------|
| Add optional field | Minor bump | Add `loyaltyNumber` to traveler |
| Add new message type | Minor bump | Add `seat-selection` intent |
| Remove field | **Major bump** | Remove `fax` from contact |
| Change field type | **Major bump** | Change `price` from number to object |
| Rename field | **Major bump** | Rename `flight` to `flightNumber` |

**Golden rule**: Unknown fields MUST be preserved, MUST NOT cause errors.

Old system receives message with new fields → processes what it knows, preserves the rest → no data loss during version mismatch.

#### E3. Extension Points

```json
{
  "data": {
    "travelers": ["..."],
    "ext": {
      "agency-crm": {
        "customerId": "CRM-789",
        "segment": "premium"
      },
      "ba-internal": {
        "revenueClass": "Q"
      }
    }
  }
}
```

Rules:
- All extensions live under `data.ext`
- Namespaced by organization
- Preserved by all processors
- Not validated against standard schema

---

### F. Compliance

#### F1. Audit Trail / Provenance Chain

UEMP uses a **dual-layer provenance model** to balance tamper-evident audit integrity with intermediary extensibility:

- **`meta.provenanceCore`** (SIGNED, immutable) — Origin events set by the message creator and covered by the payload signature. Only `created`, `converted`, and `signed` actions belong here.
- **`context.provenanceRuntime`** (UNSIGNED, mutable) — Intermediary events appended by gateways, validators, and AI processors. Actions like `validated`, `enriched`, `routed`, and `cached` belong here.

This separation ensures that compliance regimes (eIDAS Article 25, GDPR Article 30) can verify tamper-evident origin records via the payload signature, while still allowing intermediaries to append processing history without re-signing.

```json
{
  "meta": {
    "provenanceCore": [
      {
        "action": "created",
        "agent": { "id": "travel-agent-app/v4.2", "type": "software" },
        "party": { "id": "AGENCY-12345" },
        "at": "2024-03-15T08:29:50Z",
        "sourceFormat": "user-input"
      },
      {
        "action": "converted",
        "agent": { "id": "uemp-gateway/v1.0", "type": "software" },
        "at": "2024-03-15T08:29:52Z",
        "sourceFormat": "IATA-NDC/21.3",
        "targetFormat": "uemp/1.0",
        "lossless": true
      },
      {
        "action": "signed",
        "agent": { "id": "signing-service/v2.1", "type": "software" },
        "at": "2024-03-15T08:29:56Z",
        "signatureRef": "signatures[0]"
      }
    ]
  },
  "context": {
    "provenanceRuntime": [
      {
        "action": "validated",
        "agent": { "id": "schema-validator/v1.0", "type": "software" },
        "at": "2024-03-15T08:29:53Z",
        "result": "pass",
        "rulesApplied": 12
      },
      {
        "action": "enriched",
        "agent": { "id": "gemini-2.5-pro", "type": "ai-model" },
        "at": "2024-03-15T08:29:55Z",
        "changes": ["added context.summary", "added context.constraints"]
      }
    ]
  }
}
```

Note `"type": "ai-model"` — AI involvement is always recorded. Critical for AI governance regulations.

**Provenance action classification**:

| Action | Layer | Rationale |
|--------|-------|-----------|
| `created` | `meta.provenanceCore` | Origin identity — MUST be tamper-evident |
| `converted` | `meta.provenanceCore` | Format provenance — part of legal record |
| `signed` | `meta.provenanceCore` | Signing event — self-referential integrity |
| `validated` | `context.provenanceRuntime` | Post-creation check — appended by validators |
| `enriched` | `context.provenanceRuntime` | AI additions — mutable by design |
| `routed` | `context.provenanceRuntime` | Gateway routing — operational metadata |
| `cached` | `context.provenanceRuntime` | Caching event — operational metadata |

#### F2. Regulatory Compliance Markers

```json
{
  "meta": {
    "compliance": {
      "gdpr": {
        "personalData": [
          "travelers[*].name",
          "travelers[*].birthDate",
          "travelers[*].contact",
          "travelers[*].documents"
        ],
        "legalBasis": "contract-performance",
        "dataController": "AGENCY-12345",
        "retentionPeriod": "P7Y",
        "crossBorder": { "from": "GB", "to": "US", "mechanism": "adequacy-decision" }
      },
      "pciDss": {
        "scope": ["payment.card"],
        "level": "saq-a-ep"
      },
      "psd2": {
        "sca": "required",
        "exemption": null
      }
    }
  }
}
```

Every processor knows which fields need what protection.

#### F3. Environment / Test Mode

```json
{
  "meta": { "environment": "sandbox" }
}
```

| Environment | Meaning |
|------------|---------|
| `production` | Real transaction, real consequences |
| `sandbox` | Test only, never process for real |
| `test` | Functional testing (unit, integration, QA) |
| `certification` | Protocol compliance testing against conformance suite |
| `simulation` | Load/performance testing at scale with synthetic data |
| `development` | Local development — no external side effects |

All systems MUST check this flag. The `test` and `simulation` environments are semantically distinct: `test` is for functional correctness verification, `simulation` is for volumetric and performance testing with production-like load patterns.

---

### G. Internationalization

#### G1. Multi-Language Fields

```json
{
  "data": {
    "segments": [{
      "from": {
        "code": "NRT",
        "name": { "en": "Narita International Airport", "ja": "成田国際空港" }
      }
    }]
  },
  "meta": {
    "languages": { "primary": "en", "available": ["en", "ja", "fr"] }
  }
}
```

Rules:
- Multi-language fields use language-code keys
- `meta.languages.primary` is the default
- Single-language fields (person names, codes) are plain strings

---

### H. AI-Specific

#### H1. Deterministic AI Generation

**The hardest problem**: AI-generated messages must be 100% valid. LLMs hallucinate.

**Five-layer defense** (summary — see [Section 14.5](#145-ai-hallucination-in-critical-messages) for the complete deep-dive):

**Layer 1 — Schema-Constrained Output**: Use structured output / function calling to constrain generation.

**Layer 2 — Post-Generation Validation**:
```json
{
  "context": {
    "validation": {
      "schemaValid": true,
      "rulesChecked": 12,
      "rulesPassed": 11,
      "rulesFailed": [
        { "rule": "future-date", "field": "segments[0].departure", "message": "Date is in the past" }
      ]
    }
  }
}
```

**Layer 3 — Confidence Scoring**:
```json
{
  "context": {
    "generatedBy": {
      "model": "gemini-2.5-pro",
      "timestamp": "2024-03-15T08:29:55Z"
    },
    "confidence": {
      "overall": 0.94,
      "fields": {
        "travelers[0].name": 1.0,
        "travelers[0].documents[0].number": 0.72,
        "pricing.total.amount": 1.0,
        "segments[0].terminal": 0.85
      }
    }
  }
}
```

Low-confidence fields flagged for human review. Receiver decides their threshold.

**Layer 4 — Referential Validation**: Validate references against external data sources (e.g., flight numbers, airport codes via external APIs).

**Layer 5 — Confidence-Gated Processing**: Route messages based on confidence thresholds — auto-process (>=0.95), human review (0.70-0.95), or reject (<0.70).

Layers 1-3 catch ~99% of errors. Layers 4-5 catch most of the remaining 1%. See [Section 14.5](#145-ai-hallucination-in-critical-messages) for complete implementation details.

#### H2. Partial / Progressive Messages

```json
{
  "meta": {
    "completeness": "partial",
    "missingRequired": ["travelers[0].documents", "payment"]
  },
  "data": {
    "travelers": [{
      "ref": "pax-1",
      "category": "adult",
      "name": { "given": "John", "surname": "Smith" },
      "documents": { "$pending": "required before ticketing" }
    }],
    "payment": { "$pending": "required before order confirmation" }
  }
}
```

- `$pending` explicitly marks known-missing fields with explanation
- `meta.missingRequired` provides quick summary
- AI knows what to ask for next

#### H3. AI Processing Modes

```json
{
  "context": {
    "processingMode": "strict",
    "aiInstructions": {
      "interpretation": "literal",
      "ambiguityHandling": "reject-and-ask",
      "responseFormat": "structured-only"
    }
  }
}
```

| Mode | Interpretation | Ambiguity | Use Case |
|------|---------------|-----------|----------|
| `strict` | Literal only | Reject and ask | Orders, payments, legal docs |
| `standard` | Reasonable inference | Best-effort + confidence | Bookings, modifications |
| `flexible` | Full AI interpretation | Accept + note assumptions | Customer service, inquiries |

---

## 9. Schema Registry

### 9.1 Structure

```
registry/
├── profiles/
│   ├── IATA-NDC/
│   │   └── 21.3/
│   │       ├── profile.json
│   │       ├── mappings.json
│   │       ├── validation-chain.json
│   │       ├── edge-cases.json
│   │       ├── fidelity.json
│   │       └── tests/
│   ├── PEPPOL-BIS/
│   │   └── 3.0/
│   │       └── ...
│   └── ISO20022/
│       └── pain.001.001.09/
│           └── ...
├── domains/
│   ├── air-travel/
│   │   ├── domain.json
│   │   ├── messages/
│   │   │   ├── create-order.json
│   │   │   ├── shop.json
│   │   │   ├── price.json
│   │   │   └── cancel-order.json
│   │   └── codelists/
│   │       ├── cabin-class.json
│   │       ├── traveler-category.json
│   │       └── fare-type.json
│   ├── invoicing/
│   │   ├── domain.json
│   │   ├── messages/
│   │   │   ├── create-invoice.json
│   │   │   └── credit-note.json
│   │   └── codelists/
│   │       ├── invoice-type.json
│   │       └── tax-category.json
│   └── payment/
│       └── ...
├── shared/
│   ├── party.json
│   ├── amount.json
│   ├── address.json
│   ├── contact.json
│   └── document.json
└── mappings/
    ├── air-travel--IATA-NDC.json
    ├── air-travel--EDIFACT.json
    ├── invoicing--PEPPOL-BIS.json
    ├── invoicing--EDIFACT-INVOIC.json
    └── payment--ISO20022.json
```

### 9.2 Message Schema Example

> **Note**: UEMP uses a custom schema language (UEMP DSL) inspired by JSON Schema but extended with domain-specific keywords (`codelist`, `datetime`, `enum` with `values`). This is NOT standard JSON Schema — it's a UEMP-specific schema format designed for AI readability. A formal specification of this schema language will be published separately. The DSL is the reference method for domain validation (Step 5 in the validation pipeline), which is REQUIRED for Domain-Aware and Full AI conformance classes, and OPTIONAL for Core Envelope. See [Section 9.4](#94-conformance-classes).

```json
{
  "domain": "air-travel",
  "message": "create-order",
  "version": "1.0",
  "description": "Request to create a flight booking/order",
  "fields": {
    "travelers": {
      "type": "array",
      "items": { "$ref": "shared/party.json#traveler" },
      "required": true,
      "minItems": 1,
      "description": "People traveling on this booking"
    },
    "journeys": {
      "type": "array",
      "required": true,
      "items": {
        "direction": {
          "type": "enum",
          "values": ["outbound", "inbound", "multi-city"],
          "required": true
        },
        "segments": {
          "type": "array",
          "items": {
            "from": { "$ref": "#airport", "required": true },
            "to": { "$ref": "#airport", "required": true },
            "departure": { "type": "datetime", "required": true },
            "arrival": { "type": "datetime" },
            "carrier": { "type": "string", "codelist": "iata-airline", "required": true },
            "flight": { "type": "string", "required": true },
            "cabin": { "type": "enum", "codelist": "cabin-class", "required": true }
          }
        }
      }
    }
  },
  "rules": [
    { "rule": "future-date", "fields": ["journeys[*].segments[*].departure"] },
    { "rule": "age-category-match", "fields": ["travelers[*]"] },
    { "rule": "amount-equals", "fields": ["payment.amount", "pricing.total"] }
  ]
}
```

AI loads this (~200 tokens) and knows every valid field and constraint. Compare: NDC XSD (~50,000 tokens across dozens of included files).

### 9.3 Codelist Example

```json
{
  "codelist": "traveler-category",
  "domain": "air-travel",
  "values": {
    "adult": {
      "description": "Adult traveler",
      "ageRange": "12+",
      "pricingImpact": "full fare"
    },
    "child": {
      "description": "Child traveler",
      "ageRange": "2-11",
      "pricingImpact": "typically discounted 25-50%"
    },
    "infant": {
      "description": "Infant traveler",
      "ageRange": "0-2",
      "pricingImpact": "free or 10% of adult fare, no seat"
    }
  },
  "nativeProtocolMappings": {
    "IATA-NDC": { "adult": "ADT", "child": "CHD", "infant": "INF" },
    "EDIFACT": { "adult": "700", "child": "701", "infant": "702" }
  }
}
```

### 9.4 Conformance Classes

UEMP defines four conformance classes. Each class builds on the previous and adds additional requirements. Implementations MUST declare which conformance class they support.

| Class | Validation Steps | Domain Validation | Signatures | AI Enrichment | v1.0 Requirement |
|-------|-----------------|-------------------|------------|---------------|-------------------|
| **Core Envelope** | Steps 1-3 | NOT required | NOT required | NOT required | REQUIRED for all implementations |
| **Domain-Aware** | Steps 1-5 | REQUIRED | NOT required | NOT required | RECOMMENDED for production |
| **Secure** | Steps 1-4 | OPTIONAL | REQUIRED (payload profile minimum) | NOT required | REQUIRED for regulated industries |
| **Full AI** | Steps 1-6 | REQUIRED | REQUIRED | REQUIRED | OPTIONAL |

**Validation steps reference** (see [Section 9.5 Validation Pipeline](#95-validation-pipeline)):
1. JSON well-formedness (RFC 8259)
2. Size limits check
3. Envelope schema validation (Appendix C JSON Schema 2020-12)
4. Signature verification (if signatures present)
5. Domain schema validation (UEMP DSL or equivalent)
6. Business rule validation (domain rules from registry)

**Domain validation note**: Step 5 (domain schema validation) is REQUIRED for Domain-Aware and Full AI conformance classes. For Core Envelope conformance, domain validation is NOT required. The UEMP DSL is the reference method for domain validation, but implementations MAY use alternative methods (transpiled JSON Schema, custom validators) provided they produce equivalent results.

**Capability discovery**: Implementations MUST advertise their conformance class in the `/.well-known/uemp` capability document:

```json
{
  "conformanceClass": "domain-aware",
  "supportedSteps": [1, 2, 3, 4, 5]
}
```

The `supportedSteps` array lists all validation steps the implementation is *capable* of executing. For Domain-Aware class, step 4 (signature verification) MUST be listed because the implementation MUST verify signatures when the `signatures` array is present (see [Section 9.5](#95-validation-pipeline)), even though signatures are not *required* to be present for this class.

### 9.5 Validation Pipeline

UEMP processors MUST validate incoming messages through the following ordered pipeline. Each step depends on the previous step passing. The conformance class determines which steps are required (see [Section 9.4](#94-conformance-classes)).

| Step | Name | Action | Error Code on Failure |
|------|------|--------|-----------------------|
| **1** | JSON well-formedness | Parse as JSON per RFC 8259 | `protocol-malformed` |
| **2** | Size limits | Check message and field sizes against D5 limits | `protocol-message-too-large` / `protocol-field-too-large` |
| **3** | Envelope schema | Validate against Appendix C JSON Schema (2020-12) | `validation-schema-failed` |
| **4** | Signature verification | If `signatures` array is present, verify each in reverse chronological order | `protocol-signature-invalid` / `protocol-signature-expired` |
| **5** | Domain schema | Validate `data` section against the domain schema from the registry | `validation-required-field` / `validation-invalid-type` / `validation-invalid-format` / `validation-invalid-code` / `validation-constraint-failed` |
| **6** | Business rules | Apply domain-specific business rules from the registry | `business-*` codes |

**Step dependencies**:
- Steps 1-3 are REQUIRED for all conformance classes (Core Envelope minimum)
- Step 4 is REQUIRED for Secure and Full AI classes, OPTIONAL otherwise (but MUST execute if `signatures` is present)
- Step 5 is REQUIRED for Domain-Aware and Full AI classes
- Step 6 is REQUIRED for Full AI class only

**Short-circuit rule**: If any step fails with a `fatal` severity error, processing MUST stop and return the error. Steps MUST execute in order (1 → 2 → 3 → 4 → 5 → 6).

### 9.6 Protocol Profiles & Universal Coverage Framework

To support all existing enterprise protocols without overloading the core specification, UEMP uses a **profile-based coverage model**.

This section does **not** claim that all protocols are fully supported today. It defines the normative framework required to claim support consistently across XML, EDI, and mixed-rule ecosystems.

Support levels in this section are **orthogonal** to conformance classes in [Section 9.4](#94-conformance-classes): conformance class describes processor behavior; support level describes protocol/version coverage quality.

#### 9.6.1 Protocol Profile Artifact

Each native protocol/version MUST be represented by a versioned profile artifact:

```
profiles/{protocol-family}/{version}/
├── profile.json
├── mappings.json
├── validation-chain.json
├── edge-cases.json
├── fidelity.json
└── tests/
    ├── valid/
    ├── invalid/
    ├── roundtrip/
    └── signatures/
```

`profile.json` MUST declare:
- `protocolFamily` (e.g., `IATA-NDC`, `PEPPOL-BIS`, `UN-EDIFACT`, `ISO20022`)
- `protocolVersion` (e.g., `21.3`, `3.0`, `D.96A`, `pain.001.001.09`)
- supported message set (e.g., `OrderCreateRQ`, `INVOIC`, `Invoice`, `pain.001`)
- required validator adapters
- declared support level (see [Section 9.6.4](#964-support-levels))

#### 9.6.2 Validation Adapter Contract

All native validation technologies MUST be executed through a common adapter contract so outputs are normalized into UEMP error structures (Section C3).

Required adapter types:
- `xsd` — XML Schema validation
- `schematron` — rule assertions over XML instances
- `edi-grammar` — segment/loop grammar validation (EDIFACT/X12-style)
- `codelist` — code/enum validation against versioned lists
- `business-rules` — domain rules not expressible in native schema grammar
- `referential` — external reference checks (flight existence, party registries, tax IDs)

**Profile asset references (normative)**:
- Profile artifacts MUST reference bundled validation assets by stable identifiers, not host file paths.
- For Schematron stages, `validation-chain.json` MUST use `config.xsltId` (or `config.xslt_id`) that resolves via an allowlist.
- For XSD stages, profiles MAY pin the underlying structural schema set using `config.schemaSet` (allowlisted).

Adapter output MUST map to:
- `code` (UEMP error code)
- `severity`
- `field` (UEMP path syntax)
- `expected` / `actual`
- `message`
- optional `recovery`

#### 9.6.3 Mapping & Fidelity Contract

Each profile MUST publish mapping and fidelity declarations:

1. `mappings.json`:
- deterministic path mappings (`native-path` ↔ `uemp-path`)
- code translation tables (e.g., NDC `ADT` ↔ UEMP `adult`)
- explicit handling for non-isomorphic constructs (attributes/elements, namespaces, segment qualifiers)

2. `fidelity.json`:
- supported fidelity target:
  - `semantic`
  - `structural`
  - `byte` (optional)
- known non-preservable constructs, each with rationale and mitigation
- required fallback behavior when requested fidelity cannot be met

Processors MUST NOT claim structural or byte fidelity unless the profile test suite proves it for that protocol/version.

#### 9.6.4 Support Levels

A profile can claim one of the following levels:

| Level | Name | Minimum Requirements |
|------|------|----------------------|
| `L0` | Parse-Only | Native parse + envelope generation, no native validation parity claim |
| `L1` | Validation-Parity | Parse + native validation adapters + normalized UEMP errors |
| `L2` | Bidirectional Mapping | L1 + deterministic native↔UEMP conversion for declared message set |
| `L3` | Round-Trip Qualified | L2 + published round-trip test corpus + declared fidelity class per message type |
| `L4` | Production-Certified | L3 + conformance certification + edge-case coverage threshold + security/signature vectors |

Normative rule: A protocol/version MUST NOT be described as "supported" in production documentation unless it is at least `L3`.

#### 9.6.5 Edge-Case Registry

Each profile MUST maintain `edge-cases.json` entries:

| Field | Description |
|------|-------------|
| `id` | Stable case identifier (`{protocol}-{version}-{nnnn}`) |
| `appliesTo` | Message types and versions impacted |
| `trigger` | Condition that activates the case |
| `risk` | `low` / `medium` / `high` |
| `handling` | deterministic mapping, fallback, or reject |
| `tests` | linked regression test vectors |
| `status` | `open`, `mitigated`, `resolved` |

Known high-risk edge cases MUST have regression tests before a profile can reach `L4`.

#### 9.6.6 Capability Discovery Extensions

`/.well-known/uemp` SHOULD expose profile-level support metadata:

```json
{
  "profiles": [
    {
      "protocolFamily": "IATA-NDC",
      "protocolVersion": "21.3",
      "supportLevel": "L3",
      "fidelity": "semantic",
      "messageTypes": ["OrderCreateRQ", "OrderViewRS"],
      "validators": ["xsd", "business-rules"]
    }
  ]
}
```

When present, this metadata MUST reflect the latest published profile artifacts.

#### 9.6.7 Certification Test Pack

For each profile, a certification pack MUST include:
- valid native messages
- invalid native messages with expected normalized UEMP errors
- bidirectional mapping vectors
- round-trip equivalence vectors
- signature/encryption vectors (where profile declares secure support)
- edge-case regression vectors

A profile MUST publish pass/fail thresholds (e.g., minimum round-trip success percentage) and MUST include protocol-version-specific known limitations.

#### 9.6.8 Governance & Lifecycle

Profile artifacts MUST follow lifecycle states:
- `draft`
- `candidate`
- `stable`
- `deprecated`

Rules:
- `stable` artifacts are immutable (new behavior requires a new profile revision)
- compatibility-impacting changes MUST include migration notes
- deprecated profiles MUST include an end-of-support date
- certification claims MUST reference exact profile revision IDs

---

## 10. Protocol Comparison

### Where Current Protocols Are STRONGER

| Concern | Current Protocols | UEMP |
|---------|------------------|-----|
| **Digital signatures** | XML-DSIG + C14N is mature, legally proven, eIDAS-recognized | JWS/JCS exists but has less legal precedent |
| **Schema validation rigor** | XSD is extremely powerful (complex types, restrictions, inheritance) | JSON Schema is capable but less expressive |
| **Legal standing** | EDIFACT has UN recognition. UBL has EU mandate. ISO 20022 has banking regulatory backing | Zero legal precedent |
| **Ecosystem tooling** | Thousands of libraries, validators, editors | Everything built from scratch |
| **Deterministic processing** | Parser validates or rejects. Identical input = identical output | AI introduces non-determinism |
| **Non-AI consumers** | Any XML parser processes NDC | `data` section is parseable by anyone, but `context` requires AI |

### Where UEMP Is STRONGER

| Concern | Current Protocols | UEMP |
|---------|------------------|-----|
| **Cross-protocol interop** | Zero. NDC→EDIFACT is a custom project | Native. Same data, different native mapping |
| **Version migration** | Breaking change = months of rewrites | Schema delta, AI adapts automatically |
| **Error recovery** | Malformed XML = hard reject | AI reads intent + context, processes imperfect messages |
| **Onboarding cost** | EDIFACT takes months to learn. NDC XSD is thousands of lines | AI reads format natively, humans read it easily |
| **Multi-domain messages** | Impossible. Can't mix NDC and PEPPOL | Natural. Single message, multiple domains |
| **Total comprehension cost** | High (message + spec + codelists) | Low (~10x fewer tokens, self-describing) |
| **Error messages** | Cryptic codes | Field pointers + recovery instructions |

---

## 11. Strengths & Weaknesses

### Strengths

1. **10x token efficiency** for AI processing — at scale, this translates to millions in cost savings
2. **Zero-context understanding** — self-describing format needs no external documentation
3. **Cross-protocol composition** — combine travel + payment + invoicing in one message
4. **Graceful degradation** — `data` section works without AI, `context` adds AI superpowers
5. **Built-in compliance** — GDPR, PCI-DSS markers travel with the data
6. **Full audit trail** — every transformation recorded, including AI involvement
7. **Forward compatible** — unknown fields preserved, gradual adoption possible

### Weaknesses

1. **No legal standing** — courts and regulators don't recognize it (yet)
2. **No ecosystem** — every tool, library, validator must be built
3. **AI dependency for full features** — `context` section meaningless to traditional systems
4. **Governance vacuum** — no governing body, no certification process
5. **Lossless conversion not guaranteed** — edge cases in protocol mapping may lose nuance
6. **Adoption chicken-and-egg** — no value until both sender and receiver support it

---

## 12. Open Problems

These problems are acknowledged but not yet fully solved at the protocol level:

| Problem | Status | Path Forward |
|---------|--------|-------------|
| Legal equivalence with XML-DSIG | Unsolved | Requires regulatory engagement (eIDAS, UN/CEFACT) |
| AI hallucination in generation | Mitigated (5-layer defense, see [Section 14.5](#145-ai-hallucination-in-critical-messages)) | Improving with model capabilities |
| Industry governance body adoption | Not started | Requires governance and standards engagement beyond technical work |
| Performance for HFT protocols (FIX) | Out of scope | UEMP targets seconds-scale protocols, not microsecond |
| Complete lossless round-trip for all protocols | Partially solved | Edge cases need per-protocol testing |
| JSON Schema expressiveness gap vs XSD | Minor | JSON Schema draft-2020-12 closes most gaps |

---

## 13. Adoption Notes

This section is **non-normative** and focuses on protocol adoption mechanics (not product positioning, roadmaps, or implementation details).

### 13.1 Gateway-First Adoption (One-Sided Value)

UEMP can be adopted unilaterally:

- A system can convert native messages to UEMP internally for AI-friendly processing.
- It can still emit native protocols at external boundaries.
- This avoids a "both parties must adopt first" deadlock.

### 13.2 Governance (Code First)

Recommended sequence:

1. Working code and test vectors
2. Interop and conformance packs
3. Multi-party governance once multiple independent implementations exist

### 13.3 Third-Party Schema Redistribution

UEMP implementations may depend on third-party assets (XSD, Schematron, codelists) owned by standards bodies.

- Implementations MUST respect the licensing terms of each standards body.
- Public repositories SHOULD avoid bundling third-party assets unless redistribution is explicitly permitted.
- Prefer "fetch from official source" workflows over redistribution.

---

## 14. Specific Concerns Deep-Dive

This section provides exhaustive technical analysis of the 8 hardest problems facing UEMP — the ones that could kill adoption if handled poorly.

---

### 14.1 Digital Signatures & Legal Equivalence

**The concern**: EU eIDAS regulation and PEPPOL both reference XML Advanced Electronic Signatures (XAdES). If UEMP uses JWS instead of XML-DSIG, does it have legal standing?

**The answer most people don't know**: **JAdES exists.**

ETSI TS 119 182 (JSON Advanced Electronic Signatures) is the JSON equivalent of XAdES, standardized by the same body (ETSI) that standardized XAdES. It is recognized under the eIDAS framework.

```
XML world:                    JSON world:
XML-DSIG (W3C)               JWS (RFC 7515)
  └── XAdES (ETSI)             └── JAdES (ETSI TS 119 182)
       └── eIDAS recognized          └── eIDAS recognized
```

**UEMP signature stack**:

| Layer | Standard | Purpose |
|-------|----------|---------|
| Canonicalization | RFC 8785 (JCS) | Deterministic JSON serialization before signing |
| Base signature | RFC 7515 (JWS) | Core signature mechanism |
| Advanced signature | ETSI TS 119 182 (JAdES) | Long-term validation, timestamp, certificate chain |
| Qualified signature | eIDAS Article 28 | Legal equivalence with handwritten signature |

**JAdES signature in UEMP message** (includes all required base fields plus JAdES-specific extensions):

```json
{
  "signatures": [
    {
      "id": "sig-jades-qualified",
      "party": { "id": "QTSP-QUOVADIS", "role": "qualified-signer" },
      "scope": ["meta", "data"],
      "algorithm": "PS256",
      "certificate": "https://pki.quovadis.com/cert/2024-qualified.pem",
      "value": "eyJhbGciOiJQUzI1NiIsInR5cCI6Ikpvc2UiLCJ4NWMiOlsi...",
      "timestamp": {
        "authority": "http://timestamp.quovadis.com",
        "value": "2024-03-15T08:30:00Z",
        "token": "MIIHzwYJKoZIhvc..."
      },
      "profile": "JAdES-B-LTA",
      "signingTime": "2024-03-15T08:30:00Z",
      "signingCertificate": {
        "issuer": "CN=QuoVadis EU Issuing CA G3,O=QuoVadis",
        "serial": "4A:3B:2C:1D",
        "digest": "sha256:abc123..."
      }
    }
  ]
}
```

The fields `id`, `party`, `scope`, `algorithm`, and `value` are the required base envelope fields (see [Section A1](#a-security)). The fields `profile`, `signingTime`, and `signingCertificate` are JAdES-specific extensions per ETSI TS 119 182.

**Remaining gap**: While JAdES is technically eIDAS-compatible, **practical adoption is years behind XAdES**. Validation tools, trust service providers, and qualified trust lists (QTLs) predominantly support XAdES. This means:

- **Short-term (0-2 years)**: UEMP messages requiring legal signatures should carry dual signatures — JAdES in the UEMP message + XAdES in the native protocol output (gateway generates both)
- **Medium-term (2-5 years)**: As JAdES tooling matures, single JAdES signature suffices
- **Long-term**: JAdES becomes the standard for all JSON-based business documents

**Action items**:
1. Implement JAdES-B-B (baseline) signatures in UEMP core library
2. Integrate with at least one qualified TSP (Trust Service Provider) for timestamp tokens
3. Build a JAdES validation library (or wrap an existing one like DSS - Digital Signature Services)
4. Engage with ETSI TC ESI working group to ensure UEMP's signature profile is conformant

---

### 14.2 Determinism & Auditability

**The concern**: When AI processes a message, the output may vary between runs. Financial and legal contexts require identical processing — same input must produce same output, every time.

**The architectural answer**: UEMP's three-section design already solves this.

```
┌──────────────────────────────────────────────────────────────┐
│  meta + data sections                                        │
│                                                              │
│  ✅ DETERMINISTIC                                            │
│  - JSON parsing + JCS canonicalization is deterministic       │
│  - Schema validation is deterministic (JSON Schema)          │
│  - Field extraction is deterministic (JSONPath)              │
│  - Codec conversion is deterministic (rule-based mapping)    │
│                                                              │
│  → Same input ALWAYS produces same output                    │
│  → Auditable, reproducible, legally binding                  │
├──────────────────────────────────────────────────────────────┤
│  context section                                             │
│                                                              │
│  ⚠️ NON-DETERMINISTIC (by design)                           │
│  - AI-generated summaries may vary                           │
│  - Confidence scores may differ between runs                 │
│  - Enrichment depends on AI model version                    │
│                                                              │
│  → Advisory only, never legally binding                      │
│  → Unsigned, mutable, clearly separated                      │
└──────────────────────────────────────────────────────────────┘
```

**Audit architecture**:

```json
{
  "meta": {
    "provenanceCore": [
      {
        "action": "converted",
        "type": "deterministic",
        "agent": { "id": "uemp-ndc-codec/1.2.3", "type": "software" },
        "input": { "hash": "sha256:input-hash", "format": "IATA-NDC/21.3" },
        "output": { "hash": "sha256:output-hash", "format": "uemp/1.0" },
        "reproducible": true
      }
    ]
  },
  "context": {
    "provenanceRuntime": [
      {
        "action": "enriched",
        "type": "non-deterministic",
        "agent": { "id": "gemini-2.5-pro", "type": "ai-model", "version": "2024-03-01" },
        "temperature": 0.1,
        "reproducible": false,
        "affectedSections": ["context"]
      }
    ]
  }
}
```

**Key audit guarantee**: Any processor can verify that `meta` + `data` sections were produced deterministically by:
1. Re-running the codec with the same input
2. Comparing output hash
3. Hashes MUST match (deterministic guarantee)

The `context` section has no such guarantee and is explicitly marked non-deterministic. Regulators audit `meta` + `data`. AI insights in `context` are supplementary.

**Edge case — AI in the deterministic path**: What if AI is used for conversion (like your existing ConversionService that uses Gemini for NDC version conversion)?

Solution: **AI-assisted conversions are flagged as non-deterministic** and carry a validation certificate:

```json
{
  "meta": {
    "provenanceCore": [
      {
        "action": "converted",
        "type": "non-deterministic",
        "agent": { "id": "gemini-2.5-pro", "type": "ai-model" },
        "sourceFormat": "IATA-NDC/21.3",
        "targetFormat": "uemp/1.0",
        "lossless": false
      }
    ]
  },
  "context": {
    "provenanceRuntime": [
      {
        "action": "validated",
        "type": "deterministic",
        "agent": { "id": "post-conversion-validator/1.0", "type": "software" },
        "validation": {
          "postConversionXsdValid": true,
          "schematronValid": true,
          "semanticDiffScore": 0.99,
          "humanReviewRequired": false
        }
      }
    ]
  }
}
```

The AI conversion is non-deterministic, but the **validation of the output IS deterministic**. If XSD + Schematron pass, the output is structurally correct regardless of how it was generated.

---

### 14.3 Legal Standing & Regulatory Recognition

**The concern**: Courts and regulators mandate specific formats. EU Directive 2014/55/EU mandates EN 16931 for public procurement invoicing. Can UEMP ever satisfy these mandates?

**Deeper analysis** — what do regulations actually mandate?

| Regulation | What It Actually Mandates | What People Think It Mandates |
|-----------|--------------------------|------------------------------|
| EU Directive 2014/55/EU | EN 16931 **semantic data model** | "You must use UBL XML" |
| PEPPOL BIS Billing 3.0 | UBL 2.1 syntax OR CII syntax | "You must use UBL" |
| eIDAS (electronic signatures) | Qualified electronic signature (format-agnostic) | "You must use XAdES" |
| PSD2 (payment services) | Strong customer authentication (method-agnostic) | "You must use a specific format" |

**Critical insight**: EN 16931 defines a **semantic data model** — a set of business terms and rules. It explicitly specifies two syntaxes (UBL 2.1 and CII), but the **semantic model is syntax-independent**. If UEMP can represent all EN 16931 business terms with equivalent semantics, it could theoretically become a third recognized syntax.

**Pragmatic path**:

```
Phase 1: UEMP as internal format (no regulatory impact)
  UEMP message → Gateway → UBL 2.1 → PEPPOL network
  ✅ Legal: UBL output is what reaches the tax authority

Phase 2: UEMP as exchange format with bilateral agreement
  Company A → UEMP → Company B (both agree to use UEMP)
  Gateway → UBL → tax authority (regulatory compliance maintained)
  ✅ Legal: Parties can agree on any format between themselves

Phase 3: UEMP as recognized syntax for EN 16931
  Submit UEMP syntax binding to CEN TC 434 working group
  If accepted: UEMP becomes third official syntax alongside UBL and CII
  ⏳ Timeline: 3-7 years for standards process
```

**What you can do NOW**: Build the EN 16931 semantic model mapping. Prove that every EN 16931 business term (BT-1 through BT-189) maps perfectly to UEMP fields. This is the groundwork for future standardization.

```json
{
  "context": {
    "nativeMapping": {
      "EN16931": {
        "data.invoice.number": "BT-1 (Invoice number)",
        "data.invoice.issueDate": "BT-2 (Invoice issue date)",
        "data.invoice.type": "BT-3 (Invoice type code)",
        "data.invoice.currency": "BT-5 (Invoice currency code)",
        "data.seller.name": "BT-27 (Seller name)",
        "data.seller.vatId": "BT-31 (Seller VAT identifier)",
        "data.buyer.name": "BT-44 (Buyer name)",
        "data.totals.netAmount": "BT-109 (Invoice total amount without VAT)",
        "data.totals.vatAmount": "BT-110 (Invoice total VAT amount)",
        "data.totals.payableAmount": "BT-115 (Amount due for payment)"
      }
    }
  }
}
```

---

### 14.4 Lossless Round-Trip Guarantee

**The concern**: Can you PROVE that `NDC XML → UEMP → NDC XML` produces semantically equivalent output? XML has features JSON fundamentally cannot represent.

**XML features that JSON can't natively represent**:

| XML Feature | Problem | UEMP Solution |
|------------|---------|-------------|
| **Attributes vs elements** | `<Flight Number="117"/>` vs `<Flight><Number>117</Number></Flight>` — semantically different in XML | Store attribute/element distinction in `nativeMapping` |
| **Namespace declarations** | `xmlns:ns="http://..."` — no JSON equivalent | Store namespace map in `meta.source.namespaces` |
| **Processing instructions** | `<?xml-stylesheet ...?>` — no JSON equivalent | Store in `meta.source.processingInstructions` |
| **CDATA sections** | `<![CDATA[raw text]]>` — no JSON equivalent | Unnecessary in JSON (strings are always raw) |
| **Attribute ordering** | XML spec says order doesn't matter, but some systems check | Store original order in `nativeMapping` |
| **Whitespace in mixed content** | Significant whitespace between elements | Store whitespace hints if needed |
| **Entity references** | `&amp;` `&lt;` etc. | JSON handles escaping differently — store original if critical |
| **Comments** | `<!-- comment -->` — no JSON equivalent | Discard (comments are not semantically meaningful) |

**The `nativeMapping` as lossless guarantee**:

```json
{
  "context": {
    "nativeMapping": {
      "IATA-NDC/21.3": {
        "_namespaces": {
          "": "http://www.iata.org/IATA/2015/00/2021.3/IATA_OrderCreateRQ",
          "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        },
        "_rootElement": "OrderCreateRQ",
        "_attributes": {
          "OrderCreateRQ.Version": "21.3",
          "Passenger.PassengerID": "travelers[0].ref"
        },
        "travelers[0].category=adult": "Passenger/PTC=ADT",
        "travelers[0].ref=pax-1": "Passenger/@PassengerID=PAX1"
      }
    }
  }
}
```

**Formal definition of "lossless"**:

UEMP defines three levels of round-trip fidelity:

| Level | Definition | Guarantee |
|-------|-----------|-----------|
| **Semantic equivalence** | All business data preserved. Structural differences allowed (different element order, reformatted whitespace) | **Default. Required.** |
| **Structural equivalence** | Same element hierarchy, same attributes, same values. Whitespace and formatting may differ | Optional. Achievable for most protocols. |
| **Byte equivalence** | Bit-for-bit identical output | Not guaranteed. Not a goal. (XML canonicalization can achieve this if needed.) |

**Verification methodology**:

```python
# Automated round-trip test
def test_lossless_roundtrip(ndc_xml: str):
    # Forward conversion
    uemp_message = ndc_codec.to_uemp(ndc_xml)

    # Reverse conversion
    reconstructed_xml = ndc_codec.from_uemp(uemp_message)

    # Parse both XMLs
    original_tree = etree.parse(ndc_xml)
    reconstructed_tree = etree.parse(reconstructed_xml)

    # Semantic equivalence: all business data matches
    assert extract_business_data(original_tree) == extract_business_data(reconstructed_tree)

    # Structural equivalence: XSD validation produces same result
    assert validate_xsd(original_tree) == validate_xsd(reconstructed_tree)

    # Both validate against same schema
    assert xsd_schema.validate(reconstructed_tree)
```

Run this against the **178+ XML examples already in the codebase** (75 CII + 95 UBL + 8 PEPPOL) to build a comprehensive test suite.

---

### 14.5 AI Hallucination in Critical Messages

**The concern**: AI generates a flight booking with a non-existent flight number. Or maps a tax code incorrectly. Structural validation passes, but the data is semantically wrong.

**The problem has layers**:

| Layer | What Can Go Wrong | Detection |
|-------|------------------|-----------|
| **Structural** | Missing required field, wrong type | JSON Schema validation catches 100% |
| **Format** | Invalid date format, wrong currency code | Codelist + regex validation catches 100% |
| **Referential** | Non-existent flight number, invalid airport code | External reference validation (requires API calls) |
| **Semantic** | Amount doesn't match breakdown sum, dates contradict | Business rule validation catches most |
| **Factual** | Flight doesn't operate on that date, price is unrealistic | Domain knowledge validation (hardest) |

**Five-layer defense** (this section is the authoritative reference; [Section H1](#h1-deterministic-ai-generation) provides a summary):

**Layer 1 — Schema-Constrained Generation**:
```python
# Use structured output to constrain AI to valid schema
response = gemini.generate(
    prompt=conversion_prompt,
    response_schema=UEMPMessageSchema,  # Pydantic model
    temperature=settings.gemini_temperature_strict  # 0.1
)
```

**Layer 2 — Structural Validation**:
```python
# JSON Schema validation (deterministic, fast)
validator = UEMPSchemaValidator(domain="air-travel", message="create-order")
result = validator.validate(uemp_message)
# Catches: missing fields, wrong types, invalid enums
```

**Layer 3 — Business Rule Validation**:
```python
# Rule engine checks semantic constraints
rules = registry.get_rules("air-travel/create-order")
for rule in rules:
    rule.validate(uemp_message)
# Catches: amount mismatches, date contradictions, age-category mismatch
```

**Layer 4 — Referential Validation** (new):
```python
# Validate references against external data sources
async def validate_references(message: UEMPMessage):
    errors = []
    for segment in message.data.segments:
        if not await iata_api.flight_exists(segment.carrier, segment.flight, segment.departure):
            errors.append(ReferentialError(
                field=f"segments[{i}].flight",
                message=f"Flight {segment.carrier}{segment.flight} not found for {segment.departure}",
                severity="warning"  # Not fatal — API might be down
            ))
    return errors
```

**Layer 5 — Confidence-Gated Processing** (new):
```json
{
  "context": {
    "confidence": {
      "overall": 0.94,
      "fields": {
        "segments[0].flight": 0.99,
        "pricing.total.amount": 1.0,
        "travelers[0].documents[0].number": 0.72
      }
    },
    "gatingPolicy": {
      "autoProcess": { "minConfidence": 0.95 },
      "humanReview": { "minConfidence": 0.70 },
      "reject": { "below": 0.70 }
    }
  }
}
```

Processing flow:
- Field confidence >= 0.95 → auto-process
- Field confidence 0.70-0.95 → flag for human review
- Field confidence < 0.70 → reject, request re-entry
- Overall confidence below threshold → entire message goes to human review

**The honest truth**: Layers 1-3 catch ~99% of errors. Layers 4-5 catch most of the remaining 1%. But **zero hallucination is impossible** with current AI. The protocol's job is to make hallucination detectable and recoverable, not to eliminate it.

---

### 14.6 Security Attack Surface

**The concern**: A new format means new attack vectors. What can go wrong?

**Attack vector analysis**:

#### 14.6.1 `$link` as SSRF (Server-Side Request Forgery)

```json
{
  "data": {
    "attachments": [{
      "content": { "$link": "http://169.254.169.254/latest/meta-data/iam/security-credentials/" }
    }]
  }
}
```

An attacker embeds a `$link` pointing to internal cloud metadata endpoints. If the server fetches this URL, it leaks credentials.

**Mitigation**:
- `$link` URLs MUST be validated against an allowlist of trusted domains
- Private IP ranges (10.x, 172.16.x, 169.254.x, 192.168.x) MUST be blocked
- `$link` resolution MUST be optional — processors can choose not to fetch external references
- Maximum redirect depth: 0 (no redirects)
- Timeout: 5 seconds max

```json
{
  "meta": {
    "linkPolicy": {
      "allowedDomains": ["storage.company.com", "cdn.partner.com"],
      "blockPrivateIp": true,
      "maxSize": "10MB",
      "timeout": 5000
    }
  }
}
```

#### 14.6.2 Schema Registry Poisoning

An attacker compromises the schema registry and modifies a domain schema to make previously invalid messages valid (removing required fields, expanding enums).

**Mitigation**:
- Schema files MUST be signed (JWS signature on each schema file)
- Processors MUST verify schema signatures before using them
- Schema versions are immutable — once published, never modified
- Schema registry maintains an append-only audit log
- Critical schemas pinned by hash in processor configuration

```json
{
  "meta": {
    "schemaRefs": [
      {
        "domain": "air-travel",
        "version": "1.0",
        "hash": "sha256:a1b2c3d4...",
        "signature": "eyJhbGciOiJSUzI1NiJ9..."
      }
    ]
  }
}
```

#### 14.6.3 JSON Injection via Nested Encoding

```json
{
  "data": {
    "travelers": [{
      "name": { "given": "John\",\"admin\":true,\"x\":\"" }
    }]
  }
}
```

Attempting to break out of a JSON string to inject additional fields.

**Mitigation**:
- Use standard JSON parsers (not regex/string manipulation)
- All field values are typed and validated against schema
- No `eval()` or dynamic field interpretation
- Content-Security-Policy headers on API responses
- This is a non-issue with proper JSON parsing libraries (Python `json`, JS `JSON.parse`)

#### 14.6.4 Encrypted Field Oracle Attack

An attacker sends messages with manipulated `$enc` fields to observe error messages and gradually decrypt content.

**Mitigation**:
- Decryption errors MUST return generic "decryption failed" — no detailed error messages
- Rate limiting on messages with encrypted fields
- Encrypted fields use authenticated encryption (AES-GCM via JWE) which detects tampering
- Failed decryption attempts logged and monitored

#### 14.6.5 Denial of Service via Message Complexity

```json
{
  "data": {
    "travelers": [/* 1 million entries */],
    "journeys": [{ "segments": [/* deeply nested */] }]
  }
}
```

**Mitigation**:
- Maximum message size: 1 MB (enforced at transport layer)
- Maximum array length: 10,000 items
- Maximum nesting depth: 20 levels
- Maximum field count: 50,000
- Processing timeout: 30 seconds per message
- Limits configurable per deployment

#### 14.6.6 Threat Model Summary

| Attack | Severity | Likelihood | Mitigation Status |
|--------|---------|-----------|-------------------|
| SSRF via `$link` | High | Medium | Solved (allowlist + IP blocking) |
| Schema registry poisoning | Critical | Low | Solved (signed schemas + hash pinning) |
| JSON injection | Medium | Low | Non-issue (standard parsers) |
| Encrypted oracle | Medium | Low | Solved (authenticated encryption + rate limiting) |
| DoS via complexity | Medium | Medium | Solved (size/depth/count limits) |
| Man-in-the-middle | High | Low | Solved (TLS + JAdES signatures) |

---

### 14.7 Performance Analysis

**The concern**: Adding a conversion layer (native protocol ↔ UEMP) adds latency. Is the overhead acceptable?

**Estimated benchmarks** (theoretical, based on published library benchmarks for lxml vs ujson — actual numbers will be validated during PoC):

#### Parsing Performance

| Operation | XML (lxml, est.) | JSON (ujson, est.) | Expected Ratio |
|-----------|-----------|-------------|-------|
| Parse 1KB message | ~0.2ms | ~0.03ms | JSON ~7x faster |
| Parse 10KB message | ~1.5ms | ~0.15ms | JSON ~10x faster |
| Parse 100KB message | ~12ms | ~1.2ms | JSON ~10x faster |
| Validate against schema | ~5ms (XSD) | ~2ms (JSON Schema) | JSON ~2.5x faster |

> **Note**: These are order-of-magnitude estimates derived from published benchmarks of lxml 4.x and ujson 5.x on typical x86-64 hardware. Actual performance depends on hardware, library versions, message complexity, and schema size. The PoC ([Section 16](#16-proof-of-concept)) will produce validated benchmarks.

#### Codec Conversion Overhead

| Conversion | Estimated Time | Notes |
|-----------|---------------|-------|
| NDC XML → UEMP (rule-based) | ~2-5ms | Deterministic mapping, no AI |
| UEMP → NDC XML (rule-based) | ~2-5ms | Deterministic mapping, no AI |
| AI enrichment (context section) | ~500-2000ms | Gemini API call, async |
| Full pipeline: parse + convert + validate + enrich | ~510-2015ms | AI dominates |
| Full pipeline WITHOUT AI enrichment | ~6-15ms | Negligible overhead |

**Key insight**: The AI enrichment (context section) dominates latency at 500-2000ms. But it's **optional and async**. The deterministic path (parse + convert + validate) adds only 6-15ms — negligible for enterprise messaging where typical end-to-end latency is seconds to minutes.

#### Throughput (Estimated)

| Scenario | Est. Messages/sec | Bottleneck |
|----------|-------------|-----------|
| Conversion only (no AI) | ~5,000/sec/core | CPU-bound (JSON serialization) |
| With AI enrichment (async) | ~50/sec (per Gemini quota) | API rate limit |
| Batch processing (NDJSON) | ~10,000/sec/core | I/O-bound (disk/network) |

#### Memory Footprint

| Format | 10,000 messages in memory | Notes |
|--------|--------------------------|-------|
| NDC XML (etree) | ~800 MB | XML DOM is memory-heavy |
| UEMP JSON (dict) | ~200 MB | JSON objects are lighter |
| UEMP JSON (Pydantic) | ~350 MB | Pydantic adds validation overhead |

**Verdict**: UEMP is **faster** than native XML processing in every dimension. The gateway adds negligible overhead. Performance is a strength, not a concern.

---

### 14.8 Governance & Standards Politics

**The concern**: How to avoid the fate of ebXML, OAGIS, and UN/CEFACT CCL — technically sound standards that died from governance failure?

**Lessons from successful protocols**:

| Protocol | Started As | Governance Model | Why It Won |
|----------|-----------|-----------------|-----------|
| **HTTP** | One person's proposal (Tim Berners-Lee, 1989) | BDFL → IETF RFC process | Shipped working code first, standardized later |
| **JSON** | One person's discovery (Douglas Crockford, 2001) | No governance at all (just a web page) | So simple it needed no governance |
| **MQTT** | IBM internal protocol (1999) | Corporate → OASIS standard (2013) | 14 years of production use before standardization |
| **GraphQL** | Facebook internal (2012) | Corporate → Linux Foundation (2018) | 6 years of production use, massive adoption first |

**Lessons from failed protocols**:

| Protocol | Started As | Governance Model | Why It Failed |
|----------|-----------|-----------------|--------------|
| **ebXML** | UN/CEFACT + OASIS joint effort (1999) | Committee from day 1 | Design by committee, no working code, too complex |
| **OAGIS** | Open Applications Group (1995) | Industry consortium | Vendor-driven, competing interests, slow iteration |
| **SOAP** | Microsoft + IBM (1998) | W3C standard (2003) | Over-engineered, WS-* complexity explosion |
| **UN/CEFACT CCL** | UN standards body (2001) | International bureaucracy | Academic, no tooling, no developer adoption |

**The pattern**: Every successful protocol followed the same path:

```
Working code → Developer adoption → Production use → Standardization
```

Every failed protocol tried to reverse this:

```
Standardization → Committee design → Specification → Hope for adoption
```

**A governance approach based on these lessons**:

1. **Ship working implementations and test vectors first**. Avoid "spec-first" governance that blocks tooling.

2. **Run an open change process**. Use an RFC/PR-based workflow with clear compatibility rules and conformance packs.

3. **Move to neutral governance only after multi-implementation adoption**. A foundation or standards body process is most effective once multiple independent implementations exist.

4. **Anti-capture measures**:
   - Apache 2.0 license (irrevocable, no take-backs)
   - Spec + reference impl always free and open
   - No "premium" spec features (unlike some standards bodies that charge for full spec access)
   - Forkable by design — if governance fails, community can fork
   - Schema registry is decentralized (anyone can host a mirror)

---
