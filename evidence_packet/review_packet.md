# Audit Evidence Packet

This packet records evidence directly collected during the independent audit on 2026-09-29. It is limited to the pharmacovigilance repository in this workspace.

## Captured

- Automated test command: `c:/python313/python.exe -m pytest -q`; final result: 47 passed, no warnings, exit code 0. The suite was run after adding `src/__init__.py` and aligning pytest discovery with root-level tests.
- CLI command: `printf '\n' | c:/python313/python.exe app.py`; result: application banner and prompt appeared, empty input was rejected, and `EMPTY_DRUG_INPUT` was logged. This path makes no network request.
- Baseline test command before the import bridge: failed collection in all eight modules with `ModuleNotFoundError: No module named 'src'`.

## Not Captured / Not Claimed

- No live OpenFDA request was made during this audit. Mocked connector tests do not prove current external service availability.
- No screenshots or deployment proof were captured; this is a local CLI application, not a browser deployment.
- The checked-in `evidence_output.json` was not independently regenerated or source-verified. Its real-world vs synthetic status remains unknown.
- No evidence about the other three capability repositories is included because they were absent from the workspace.

See [verification.md](verification.md) for command evidence and [review_packets/](../review_packets/) for capability-level findings.
