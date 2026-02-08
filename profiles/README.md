# UEMP Profiles

This folder contains public-safe profile artifact schemas and example profile artifact sets.

## Schemas

`open/profiles/schemas/` contains JSON Schemas for the standard profile artifact files:

- `profile.schema.json` (for `profile.json`)
- `mappings.schema.json` (for `mappings.json`)
- `validation-chain.schema.json` (for `validation-chain.json`)
- `fidelity.schema.json` (for `fidelity.json`)
- `edge-cases.schema.json` (for `edge-cases.json`)

## Example

Examples under `open/profiles/examples/` are minimal, non-production profile artifact sets:

- `open/profiles/examples/minimal/` (iata-ndc/21.3)
- `open/profiles/examples/peppol-bis-billing__3.0/` (peppol-bis-billing/3.0)
- `open/profiles/examples/en16931-ubl__1.3/` (en16931-ubl/1.3)
- `open/profiles/examples/en16931-cii__1.3/` (en16931-cii/1.3)
- `open/profiles/examples/xrechnung-cii__3.0/` (xrechnung-cii/3.0)
- `open/profiles/examples/iso20022__MR2019/` (iso20022/MR2019)

## Validation CLI (private repo)

In the private repo, the validator CLI is implemented as:

```bash
cd backend
venv/bin/python3.13 -m app.cli.uemp profile validate --path ../open/profiles/examples/minimal
```
