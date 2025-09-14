# AC — S1.6a Packaging, smoke, SBOM

- ✅ pipx/packaging scaffold present (`pyproject.toml`, console entry)
- ✅ Local smoke script runs `init/check/report` on temp repo
- ✅ SBOM lockfile-only execution (MPI) and component counts surfaced
- ✅ Prompt CLI `genticode prompt scan --write-manifest` writes manifest

Artifacts:
- `.genticode/report.json` (generated via `genticode check`)
- `.genticode/report.html`, `.genticode/sarif.json` (via `genticode report`)

Notes:
- SBOM delta gating is partially implemented (presence + counts). Budget-based gate remains to be wired in CI policy.
- External tool verification emits gracefully when tools are missing.
