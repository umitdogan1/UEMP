# Certification Status

**Last updated**: 2026-02-11

This status tracks public certification packs and their regression-gate state.

## Implemented Packs

| Profile | Pack Path | Regression Gate |
|---|---|---|
| `iata-ndc/21.3` | `certification/packs/iata-ndc__21.3/pack.json` | Enabled |
| `peppol-bis-billing/3.0` | `certification/packs/peppol-bis-billing__3.0/pack.json` | Enabled |

## Gate Behavior

- Pack structure + fixtures are validated in CI.
- Runner unit tests must pass.
- Any change that breaks pack expectations fails CI.

## How To Reproduce

```bash
cd reference/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python certify.py --base-url http://localhost:8000 --pack ../../certification/packs/iata-ndc__21.3/pack.json
python certify.py --base-url http://localhost:8000 --pack ../../certification/packs/peppol-bis-billing__3.0/pack.json
```

Each run writes:
- `report.json`
- `report.md`

