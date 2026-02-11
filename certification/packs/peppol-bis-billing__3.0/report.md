# UEMP Certification Report

- packId: `peppol-bis-billing/3.0::cert-pack`
- profileId: `peppol-bis-billing/3.0`
- baseUrl: `http://testserver`
- endpoint: `/api/uemp/validate-native`
- startedAt: `2026-02-11T06:36:37.888440Z`
- finishedAt: `2026-02-11T06:36:38.129342Z`

## Summary

- total: 2
- passed: 2
- failed: 0

## Results

- PASS: `invoice-valid-base-example` (Invoice valid base example)
  - fixture: `fixtures/valid/base-example.xml`
  - http: 200 (expected 200)
  - valid: True (expected True)
- PASS: `invoice-minimal-invalid` (Invoice minimal invalid)
  - fixture: `fixtures/invalid/invoice_minimal_invalid.xml`
  - http: 200 (expected 200)
  - valid: False (expected False)
