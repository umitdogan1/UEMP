from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field


class CertExpectation(BaseModel):
    httpStatus: int = Field(..., ge=100, le=599)
    valid: bool


class CertCase(BaseModel):
    id: str = Field(..., min_length=1)
    title: str | None = None
    fixture: str = Field(..., min_length=1)
    expect: CertExpectation


class CertPack(BaseModel):
    packVersion: str = Field(..., min_length=1)
    packId: str = Field(..., min_length=1)
    profileId: str = Field(..., min_length=1)
    revisionId: str | None = None
    endpoint: str = Field("/api/uemp/validate-native", min_length=1)
    notes: str | None = None
    cases: list[CertCase] = Field(..., min_length=1)


class CaseResult(BaseModel):
    caseId: str
    title: str | None = None
    fixture: str
    passed: bool
    httpStatus: int
    expectedHttpStatus: int
    expectedValid: bool
    actualValid: bool | None = None
    error: str | None = None


class ReportSummary(BaseModel):
    total: int
    passed: int
    failed: int


class CertReport(BaseModel):
    reportVersion: str = "1.0"
    packId: str
    profileId: str
    revisionId: str | None = None
    baseUrl: str
    endpoint: str
    startedAt: str
    finishedAt: str
    results: list[CaseResult]
    summary: ReportSummary


@dataclass(frozen=True)
class LoadedPack:
    pack: CertPack
    pack_path: Path
    pack_dir: Path


def load_pack(pack_json_path: str | Path) -> LoadedPack:
    p = Path(pack_json_path).resolve()
    pack_obj = json.loads(p.read_text(encoding="utf-8"))
    pack = CertPack.model_validate(pack_obj)
    return LoadedPack(pack=pack, pack_path=p, pack_dir=p.parent)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _join_url(base_url: str, path: str) -> str:
    b = (base_url or "").rstrip("/")
    p = (path or "").strip()
    if not p.startswith("/"):
        p = "/" + p
    return b + p


def _render_report_md(report: CertReport) -> str:
    lines: list[str] = []
    lines.append(f"# UEMP Certification Report")
    lines.append("")
    lines.append(f"- packId: `{report.packId}`")
    lines.append(f"- profileId: `{report.profileId}`")
    if report.revisionId:
        lines.append(f"- revisionId: `{report.revisionId}`")
    lines.append(f"- baseUrl: `{report.baseUrl}`")
    lines.append(f"- endpoint: `{report.endpoint}`")
    lines.append(f"- startedAt: `{report.startedAt}`")
    lines.append(f"- finishedAt: `{report.finishedAt}`")
    lines.append("")
    lines.append(f"## Summary")
    lines.append("")
    lines.append(f"- total: {report.summary.total}")
    lines.append(f"- passed: {report.summary.passed}")
    lines.append(f"- failed: {report.summary.failed}")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        title = f" ({r.title})" if r.title else ""
        lines.append(f"- {status}: `{r.caseId}`{title}")
        lines.append(f"  - fixture: `{r.fixture}`")
        lines.append(f"  - http: {r.httpStatus} (expected {r.expectedHttpStatus})")
        lines.append(f"  - valid: {r.actualValid} (expected {r.expectedValid})")
        if r.error:
            lines.append(f"  - error: {r.error}")
    lines.append("")
    return "\n".join(lines)


async def run_pack(
    *,
    base_url: str,
    pack_json_path: str | Path,
    timeout_s: float = 30.0,
    client: httpx.AsyncClient | None = None,
) -> tuple[CertReport, str]:
    loaded = load_pack(pack_json_path)
    pack = loaded.pack

    started = _utc_now_iso()
    results: list[CaseResult] = []

    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=timeout_s)
        close_client = True

    try:
        for case in pack.cases:
            fixture_path = (loaded.pack_dir / case.fixture).resolve()
            try:
                xml = fixture_path.read_text(encoding="utf-8")
            except Exception as e:
                results.append(
                    CaseResult(
                        caseId=case.id,
                        title=case.title,
                        fixture=case.fixture,
                        passed=False,
                        httpStatus=0,
                        expectedHttpStatus=case.expect.httpStatus,
                        expectedValid=case.expect.valid,
                        actualValid=None,
                        error=f"fixture-read-failed: {e}",
                    )
                )
                continue

            url = _join_url(base_url, pack.endpoint)
            payload: dict[str, Any] = {"profileId": pack.profileId, "xml": xml}
            if pack.revisionId:
                payload["revisionId"] = pack.revisionId
            try:
                resp = await client.post(url, json=payload)
                actual_status = int(resp.status_code)
                actual_valid: bool | None = None
                err: str | None = None

                if resp.headers.get("content-type", "").startswith("application/json"):
                    try:
                        body = resp.json()
                        if isinstance(body, dict):
                            v = body.get("valid")
                            if isinstance(v, bool):
                                actual_valid = v
                    except Exception as e:
                        err = f"response-json-parse-failed: {e}"

                passed = (actual_status == case.expect.httpStatus) and (
                    actual_valid == case.expect.valid
                )

                results.append(
                    CaseResult(
                        caseId=case.id,
                        title=case.title,
                        fixture=case.fixture,
                        passed=bool(passed),
                        httpStatus=actual_status,
                        expectedHttpStatus=case.expect.httpStatus,
                        expectedValid=case.expect.valid,
                        actualValid=actual_valid,
                        error=err,
                    )
                )
            except Exception as e:
                results.append(
                    CaseResult(
                        caseId=case.id,
                        title=case.title,
                        fixture=case.fixture,
                        passed=False,
                        httpStatus=0,
                        expectedHttpStatus=case.expect.httpStatus,
                        expectedValid=case.expect.valid,
                        actualValid=None,
                        error=f"request-failed: {e}",
                    )
                )
    finally:
        if close_client and client is not None:
            await client.aclose()

    finished = _utc_now_iso()
    total = len(results)
    passed_n = sum(1 for r in results if r.passed)
    failed_n = total - passed_n

    report = CertReport(
        packId=pack.packId,
        profileId=pack.profileId,
        revisionId=pack.revisionId,
        baseUrl=base_url,
        endpoint=pack.endpoint,
        startedAt=started,
        finishedAt=finished,
        results=results,
        summary=ReportSummary(total=total, passed=passed_n, failed=failed_n),
    )

    md = _render_report_md(report)
    return report, md
