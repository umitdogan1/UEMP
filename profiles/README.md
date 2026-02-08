# UEMP Profiles

This folder contains public-safe profile artifact schemas and example profile artifact sets.

## Asset IDs

Profiles should reference bundled validator assets by stable identifiers (not host file paths):

- Schematron allowlist: `profiles/SCHEMATRON_ASSETS.md`
- XSD schemaSet allowlist: `profiles/XSD_SCHEMA_SETS.md`

## Schemas

`profiles/schemas/` contains JSON Schemas for the standard profile artifact files:

- `profile.schema.json` (for `profile.json`)
- `mappings.schema.json` (for `mappings.json`)
- `validation-chain.schema.json` (for `validation-chain.json`)
- `fidelity.schema.json` (for `fidelity.json`)
- `edge-cases.schema.json` (for `edge-cases.json`)

## Example

Examples under `profiles/examples/` are minimal, non-production profile artifact sets:

- `profiles/examples/minimal/` (iata-ndc/21.3)
- `profiles/examples/peppol-bis-billing__3.0/` (peppol-bis-billing/3.0)
- `profiles/examples/en16931-ubl__1.3/` (en16931-ubl/1.3)
- `profiles/examples/en16931-cii__1.3/` (en16931-cii/1.3)
- `profiles/examples/xrechnung-cii__3.0/` (xrechnung-cii/3.0)
- `profiles/examples/iso20022__MR2019/` (iso20022/MR2019)

## Validation

These artifacts are JSON Schema-validatable. Use any Draft 2020-12 compatible JSON Schema validator.
