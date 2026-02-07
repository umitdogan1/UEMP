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

`open/profiles/examples/minimal/` is a minimal, non-production profile artifact set used for validation testing.

## Validation CLI (private repo)

In the private repo, the validator CLI is implemented as:

```bash
cd backend
venv/bin/python3.13 -m app.cli.uemp profile validate --path ../open/profiles/examples/minimal
```

