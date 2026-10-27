# Optional Langfuse monitoring (Python SDK v4)

The financial research API remains fully usable without Langfuse. No Langfuse
account, network call or telemetry is required by default.

## Enable only after a Langfuse project is provisioned

Install `requirements-engineering.txt` and provide the following variables via
your deployment's secret manager (never commit their values):

- `LANGFUSE_TRACING_ENABLED=1`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_BASE_URL` (e.g. the URL of your self-hosted instance)

`api/analyze.py` emits an observation named `financial.api.analyze`.
The wrapper deliberately omits request contents, output bodies, email addresses
and account/financial data. Missing credentials or exporter failure cannot break
analysis responses. Opt-out by removing `LANGFUSE_TRACING_ENABLED`.

## Verification boundaries

- CI exercises opt-out, a fake SDK client, and connection failures **offline**.
- These tests prove safe integration behavior only; they do **not** verify a
  live Langfuse project, network ingestion, or an exported production trace.
- Mark full Langfuse monitoring Verified only after receiving a real trace in
  an approved project and checking that sensitive fields are absent.

A local Langfuse Docker Compose installation is possible but requires its
database, ClickHouse, cache and object store. See the official Langfuse
self-hosting guide; do not deploy paid cloud infrastructure without approval.
