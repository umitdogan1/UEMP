from __future__ import annotations

import argparse
import json
from pathlib import Path

from uemp_certification import run_pack


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="certify", description="Run a UEMP certification pack")
    p.add_argument("--base-url", required=True, help="Base URL of the UEMP implementation (e.g. http://localhost:8000)")
    p.add_argument("--pack", required=True, help="Path to pack.json")
    p.add_argument("--timeout-s", type=float, default=30.0, help="HTTP timeout in seconds")
    args = p.parse_args(argv)

    pack_path = Path(args.pack).resolve()
    report_path = pack_path.parent / "report.json"
    report_md_path = pack_path.parent / "report.md"

    import asyncio

    report, md = asyncio.run(
        run_pack(base_url=str(args.base_url), pack_json_path=str(pack_path), timeout_s=float(args.timeout_s))
    )

    report_path.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True), encoding="utf-8")
    report_md_path.write_text(md, encoding="utf-8")

    print(f"total={report.summary.total} passed={report.summary.passed} failed={report.summary.failed}")
    print(f"wrote: {report_path}")
    print(f"wrote: {report_md_path}")

    return 0 if report.summary.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

