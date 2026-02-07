# UEMP Python Reference (Public)

This is a minimal reference implementation for UEMP envelope validation and
capability discovery.

## Included

- `uemp_schemas.py`: UEMP constants and Pydantic models
- `uemp_api.py`: FastAPI endpoints (`/.well-known/uemp`, `/api/uemp/messages`, `/api/uemp/capabilities`)
- `test_uemp_endpoints.py`: Basic endpoint and strict-token tests

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn uemp_api:app --reload --port 8000
```

## Test

```bash
pytest -q
```
