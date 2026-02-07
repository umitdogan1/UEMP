# UEMP Rename Mapping (AIP -> UEMP)

**Purpose**: Define a direct, no-compatibility migration from `AIP` naming to `UEMP` naming across protocol spec, wire artifacts, APIs, and ecosystem assets.

---

## 1. Naming Targets

- **Protocol canonical name**: `UEMP`
- **Legacy name**: `AIP` (documentation history only, not accepted on wire)

Normative rule: implementations MUST use `UEMP` identifiers only. Legacy `AIP` identifiers are not accepted.

---

## 2. Canonical Identifier Mapping

| Surface | Legacy (AIP) | Canonical (UEMP) | Rule |
|---|---|---|---|
| Protocol string in `meta.protocol` | `aip/1.0` | `uemp/1.0` | MUST emit and accept only `uemp/1.x` |
| Message ID prefix | `aip:{party}:{year}:{id}` | `uemp:{party}:{year}:{id}` | MUST emit and accept only `uemp:` |
| Media type | `application/vnd.aip+json` | `application/vnd.uemp+json` | MUST accept only `application/vnd.uemp+json` (or `application/json` fallback if explicitly enabled) |
| Versioned media type | `application/vnd.aip.v1+json` | `application/vnd.uemp.v1+json` | MUST emit and accept only UEMP form |
| Well-known discovery path | `/.well-known/aip` | `/.well-known/uemp` | MUST expose only `/.well-known/uemp` |
| HTTP headers | `AIP-*` | `UEMP-*` | MUST emit and accept only `UEMP-*` |
| SSE event name | `aip-message` | `uemp-message` | MUST emit only `uemp-message` |
| API base path | `/api/aip` | `/api/uemp` | MUST expose only `/api/uemp` |
| Schema `$id` base | `https://aip-protocol.org/schema/...` | `https://uemp.org/schema/...` | MUST publish only UEMP canonical IDs |
| Registry org label | `aip-*` | `uemp-*` | New repos/docs/artifacts MUST use `uemp-*` |

---

## 3. Cutover Plan (No Backward Compatibility)

## Step 1 - Token Replacement

Replace all wire and schema tokens in one release:

- `aip/1.x` -> `uemp/1.x`
- `aip:` -> `uemp:`
- `application/vnd.aip+json` -> `application/vnd.uemp+json`
- `AIP-*` -> `UEMP-*`
- `/.well-known/aip` -> `/.well-known/uemp`
- `/api/aip/*` -> `/api/uemp/*`
- `aip-message` -> `uemp-message`

## Step 2 - Contract Enforcement

- Reject all `AIP` wire tokens.
- Reject legacy API and discovery paths.
- Return structured migration errors (see section 5).

## Step 3 - Documentation Sync

- All examples, schema IDs, and SDK references use `UEMP` only.
- Keep "AIP" only in historical notes/changelog context.

---

## 4. Wire-Level Rules (Normative)

1. Parsers MUST reject legacy token family values:
- `aip/1.x`
- `aip:` IDs
- `application/vnd.aip+json`
- `AIP-*` headers

2. Responders MUST emit only UEMP tokens:
- `meta.protocol = uemp/1.x`
- `uemp:` message IDs
- `application/vnd.uemp+json`
- `UEMP-*` headers

3. Signature verification remains strict:
- canonicalization input is exact payload received
- failed verification MUST NOT be rewritten or normalized before verification

---

## 5. Error Handling for Legacy Tokens

Use explicit protocol errors:

- `protocol-unknown-token-family`
- `protocol-invalid-version`

Example:

```json
{
  "code": "protocol-unknown-token-family",
  "severity": "fatal",
  "message": "Token family 'aip' is not supported",
  "recovery": {
    "action": "upgrade-client",
    "hint": "Use uemp/1.0 and application/vnd.uemp+json"
  }
}
```

---

## 6. Spec Edit Checklist

Required updates across spec and artifacts:

- Title/subtitle naming (`AIP` -> `UEMP`, with optional historical note)
- Media type sections and examples
- `meta.protocol` regex/pattern
- Message ID grammar examples
- HTTP header examples
- Discovery path examples
- API endpoint examples in PoC section
- Appendix schema `$id` and protocol pattern
- Glossary entries (`UEMP` canonical, `AIP` legacy/historical)

---

## 7. Domain Strategy

- **Protocol org site**: `uemp.org` (canonical)
- **Product site**: `weaveforge.com`
- Legacy docs URL (if exists): redirect to canonical UEMP docs.
