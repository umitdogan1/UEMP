# UEMP Certification Packs (Public)

This folder contains **certification packs**: reproducible test vectors (fixtures + assertions)
that can be executed against a UEMP implementation.

## What A Certification Pack Is

A pack is a directory containing:

- `pack.json`: pack metadata and case list
- `fixtures/`: native messages used as test inputs (XML, etc.)
- `PROVENANCE.json`: source and licensing notes for fixtures

The pack runner is provided in `reference/python/` so it can be executed without
depending on any product/private code.

## Run (Python)

```bash
cd reference/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run a pack against an implementation:
python certify.py \
  --base-url http://localhost:8000 \
  --pack ../../certification/packs/peppol-bis-billing__3.0/pack.json
```

The runner prints a summary and writes two files next to the pack:

- `report.json`
- `report.md`

## Packs Included

- `packs/iata-ndc__21.3/` (IATA NDC 21.3)
- `packs/peppol-bis-billing__3.0/` (Peppol BIS Billing 3.0)

See `CERTIFICATION_STATUS.md` for current pack + gate status.
