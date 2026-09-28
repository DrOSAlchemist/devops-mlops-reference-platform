# Architecture

Platform Guard is a local-first reference platform with a small Python policy engine and optional HTTP wrapper. The same scanner powers the CLI and `/scan` endpoint; `/health` supports readiness/liveness probes and `/metrics` exposes counters for Prometheus.

```text
YAML workflow ──> policy scanner ──> findings (text / JSON)
                        │
                        ├── CLI: platform-guard scan
                        └── HTTP: POST /scan ──> Prometheus metrics

CSV cost sample ──> FinOps report ──> service totals + optional budget status
```

The repo also contains isolated Terraform examples for private artifact storage on AWS, Azure, and GCP; a hardened container; a Helm deployment; and sample Prometheus alerts and Grafana panels. These are reviewable patterns, not a live multi-cloud deployment.