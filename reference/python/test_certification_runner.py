from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx

from uemp_certification import load_pack, run_pack


def _tmp_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    (pack_dir / "fixtures").mkdir(parents=True)
    (pack_dir / "fixtures" / "x.xml").write_text("<X/>", encoding="utf-8")

    (pack_dir / "pack.json").write_text(
        json.dumps(
            {
                "packVersion": "1.0",
                "packId": "example/1.0::cert-pack",
                "profileId": "example/1.0",
                "revisionId": "R1",
                "endpoint": "/api/uemp/validate-native",
                "cases": [
                    {
                        "id": "c1",
                        "title": "case 1",
                        "fixture": "fixtures/x.xml",
                        "expect": {"httpStatus": 200, "valid": True},
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return pack_dir / "pack.json"


def test_load_pack_round_trips(tmp_path: Path) -> None:
    pack_path = _tmp_pack(tmp_path)
    loaded = load_pack(pack_path)
    assert loaded.pack.packId == "example/1.0::cert-pack"
    assert loaded.pack.profileId == "example/1.0"
    assert loaded.pack.endpoint == "/api/uemp/validate-native"
    assert loaded.pack.cases[0].fixture == "fixtures/x.xml"


def test_run_pack_with_mock_transport(tmp_path: Path) -> None:
    pack_path = _tmp_pack(tmp_path)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/uemp/validate-native"
        return httpx.Response(200, json={"valid": True, "errors": [], "stages": []})

    transport = httpx.MockTransport(handler)
    async def _run() -> tuple:
        async with httpx.AsyncClient(transport=transport) as client:
            return await run_pack(
                base_url="http://example.test",
                pack_json_path=pack_path,
                client=client,
            )

    report, md = asyncio.run(_run())

    assert report.summary.total == 1
    assert report.summary.failed == 0
    assert "UEMP Certification Report" in md
