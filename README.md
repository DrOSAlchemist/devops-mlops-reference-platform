# DevOps / MLOps Reference Platform

A local-first portfolio project that connects AI workflow guardrails, cloud operations, SRE practices, and multi-cloud infrastructure examples. The scanner runs locally with sample YAML; cloud templates are opt-in and do not provision anything unless an operator supplies credentials and runs Terraform.

## Quick start

Requires Python 3.10 or newer.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

platform-guard scan examples/workflows/guarded-agent.yaml
platform-guard scan examples/workflows/unguarded-agent.yaml --format json
platform-guard cost-report examples/finops/usage.csv --budget-usd 50
pytest -q
```

The guarded Azure OpenAI, AWS Bedrock, and Google Vertex AI samples should pass. They demonstrate a provider-neutral policy contract and do not invoke vendor APIs. The unguarded sample intentionally triggers findings for model pinning, tool access, input controls, output validation, PII handling, human approval, cost limits, iteration bounds, and secret redaction.

## Policy rules

| Rule | Check |
| --- | --- |
| `MOD001` | Explicit model provider, ID, and revision |
| `TOOL001` | Non-empty tool allowlist |
| `INP001` / `INP002` | Input validation and prompt-injection screening declarations |
| `OUT001` | Output schema declaration |
| `DAT001` | PII handling set to `redact` or `deny` |
| `GOV001` / `GOV002` | Approval for high-risk workflows and valid risk level |
| `BUD001` / `LIM001` | Positive per-run budget and bounded steps |
| `OBS001` | Secret redaction enabled for telemetry |

The scanner checks declared policy configuration; it does not inspect model internals or prove that a provider's prompt-injection filter works.

## Local API

```sh
platform-guard serve --host 127.0.0.1 --port 8080
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/metrics
curl -X POST http://127.0.0.1:8080/scan \
  -H 'Content-Type: application/yaml' \
  --data-binary @examples/workflows/guarded-agent.yaml
```

The API keeps submitted workflows in memory only and emits redacted structured scan summaries, not request bodies. It is a demonstrator, not an internet-facing production service. The policy schema is provider-neutral; Azure OpenAI, AWS Bedrock, and Google Vertex AI examples are configuration examples only and do not call vendor APIs.

## Automation scripts

`scripts/verify.sh` and `scripts/verify.ps1` run the local lint, test, and source-security checks. `examples/automation/service-health.sh` probes an HTTP health endpoint. `examples/automation/iis-health-check.ps1` checks an IIS site, app pool, and HTTP response without restarting or changing services.

## Capability map

| Area | Project evidence |
| --- | --- |
| Infrastructure as code | Separate Terraform examples for AWS S3, Azure Blob Storage, and GCP Cloud Storage with private-access defaults and cost labels. |
| CI/CD & DevOps | GitHub Actions is executable CI; GitLab CI, Jenkins, and CircleCI templates show equivalent verification stages. |
| Containers & orchestration | Non-root Python container and a Helm chart with probes, resource limits, disabled token mounting, and restricted container security context. |
| Monitoring & observability | Prometheus request/finding counters, alert rules, and a Grafana starter dashboard. |
| Scripting & automation | CLI for workflow policy scans and CSV-based cost summaries. |
| ML/MLOps | Model revision, tool allowlist, input/output validation, approval, budget, and iteration checks for AI workflow YAML; a digest-pinned canary-release manifest. |
| Security & FinOps | Deterministic configuration findings, secret-redaction policy, pinned-image sample, dependency scanning, and budget threshold reporting. |
| LLM & GenAI | Guarded and intentionally unsafe agent workflow examples that show policy differences. |

## Cloud infrastructure examples

Each provider directory under `infra/terraform/` is independent. Review provider authentication, IAM, naming, region, encryption, networking, retention, and estimated spend before use.

```sh
cd infra/terraform/aws   # or azure / gcp
terraform init
terraform fmt -check
terraform validate
terraform plan -var='region=us-east-1' -var='bucket_name=replace-with-unique-name'
```

The Azure and GCP examples require their own variables. The workflow is intentionally plan-first; no cloud credentials, state files, or resource IDs are stored in this repository. Review the plan before any `terraform apply`; creating cloud resources may incur charges. Helm, Terraform formatting, and provider validation run in the `infrastructure` GitHub Actions job because those CLIs may not be installed locally.

The model-release manifest in `examples/mlops/` documents artifact digests, canary traffic, human approval and rollout gates. It is a reference contract, not an executable deployment controller. See [SLO and incident guidance](docs/slo-playbook.md).

## Validation

```sh
ruff check .
pytest -q
pip-audit
bandit -q -r src/platform_guard
```

See [architecture](docs/architecture.md) and [security model](docs/security-model.md) for scope and limitations. Project and Git commit timestamps are genuine; no history rewriting is used to imply an earlier start date.