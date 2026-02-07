# UEMP Open Repository

This directory is the curated public subtree for the `UEMP` repository.

Internal documents must never be copied here directly. Publish only content that is explicitly approved for open-source release.

## Contents

- `LICENSE`: Public license for this subtree.
- `spec/README.md`: Public specification status and publishing policy.

## Publishing

```bash
PUBLISH_PREFIX=open BRANCH=main REMOTE=uemp ./scripts/publish_uemp.sh
```

Use GitHub Actions workflow `.github/workflows/publish-uemp.yml` with `prefix=open`.
The workflow is intentionally restricted to `open/` so internal docs cannot be published by mistake.
