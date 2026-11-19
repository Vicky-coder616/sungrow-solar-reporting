# Sungrow Solar Reporting

> **Portfolio reconstruction / demonstration.** This is a reference implementation based on a described project, not a verified copy of original production source or evidence of deployment.

## Problem and purpose

Offline monthly energy reporting with an illustrative API adapter. This demo makes the workflow reproducible with synthetic data or mocked API responses and exposes the assumptions that need review before real use.

## Stack and flow

Python, requests, python-dotenv.

Normalized JSON readings -> date/site/finite-value validation -> site-month aggregation -> demonstration CSV.

`src/` contains processing code, `tests/` contains offline regression tests, `.github/workflows/checks.yml` runs offline checks on pushes and pull requests. Samples are synthetic; `output/` and runtime files are ignored.

## Setup and execution

Use Python 3.12 and an isolated virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python -m src.report --input samples/sites.json --month 2026-10 --output output/edms.csv
```

`requirements.txt` records direct dependencies; `requirements.lock` pins the resolved runtime set. Offline transformations/tests do not require API credentials after installation. No API or email call is executed automatically.

## Implemented behavior and example output

Synthetic October output: DEMO-001=80.6 and DEMO-002=51.3 kWh. Duplicate site/day readings and malformed records are rejected, including records outside the requested month. Adapter tests use injected HTTP mocks; HTTPS and timeouts are enforced.

## Tests

```powershell
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

The suite uses synthetic files and mocked service responses. See the preparation validation report for actual results and environment limitations; a workflow file is not evidence of a completed GitHub Actions run.

## Limitations and future work

The generic bearer adapter is not a verified iSolarCloud authentication/endpoint contract. CSV is not a confirmed EDMS format. No scheduler, email send or operational logging pipeline is implemented. Historical source candidates remain separate pending provenance review. Future work: approved vendor mapping, scheduling and delivery with mocked integration tests.

## Data and publication

Do not commit real customer records, tokens, production identifiers, proprietary drawings, pricing data or personal photos. Keep `.env` local. Error messages from the adapter omit request URLs and credential values. Local file paths/messages can still reveal context; review logs before sharing.

This repository contains a reconstructed demonstration prepared for a public engineering portfolio. See `docs/PROVENANCE.md` for its origin and limits. No original employer/client implementation is included. No license is granted by this publication; third-party dependencies retain their own license terms.
