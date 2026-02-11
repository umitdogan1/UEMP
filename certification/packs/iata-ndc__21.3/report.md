# UEMP Certification Report

- packId: `iata-ndc/21.3::cert-pack`
- profileId: `iata-ndc/21.3`
- baseUrl: `http://testserver`
- endpoint: `/api/uemp/validate-native`
- startedAt: `2026-02-11T06:36:37.453744Z`
- finishedAt: `2026-02-11T06:36:37.888017Z`

## Summary

- total: 2
- passed: 2
- failed: 0

## Results

- PASS: `airshoppingrq-valid-smoke` (AirShoppingRQ valid smoke)
  - fixture: `fixtures/valid/airshoppingrq_valid.xml`
  - http: 200 (expected 200)
  - valid: True (expected True)
- PASS: `airshoppingrq-minimal-invalid` (AirShoppingRQ minimal invalid)
  - fixture: `fixtures/invalid/airshoppingrq_minimal_invalid.xml`
  - http: 200 (expected 200)
  - valid: False (expected False)
