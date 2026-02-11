from __future__ import annotations

import sys
from pathlib import Path

from uemp_certification import load_pack


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    packs_root = repo_root / "certification" / "packs"
    if not packs_root.exists():
        print(f"missing packs root: {packs_root}", file=sys.stderr)
        return 2

    pack_paths = sorted(packs_root.rglob("pack.json"))
    if not pack_paths:
        print("no packs found", file=sys.stderr)
        return 2

    errors: list[str] = []
    for pack_path in pack_paths:
        try:
            loaded = load_pack(pack_path)
        except Exception as e:
            errors.append(f"{pack_path}: invalid pack.json: {e}")
            continue

        for case in loaded.pack.cases:
            fixture = (loaded.pack_dir / case.fixture).resolve()
            if not fixture.exists():
                errors.append(f"{pack_path}: missing fixture for case {case.id}: {case.fixture}")
                continue
            try:
                _ = fixture.read_text(encoding="utf-8")
            except Exception as e:
                errors.append(f"{pack_path}: unreadable fixture for case {case.id}: {case.fixture}: {e}")

    if errors:
        print("certification pack validation FAILED", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 2

    print(f"OK: {len(pack_paths)} pack(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

