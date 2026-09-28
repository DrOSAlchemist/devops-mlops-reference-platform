# Security model

Platform Guard is a policy linter and teaching reference, not a complete AI security product. Its findings are deterministic checks over declared workflow configuration; it does not inspect model internals, prove prompt-injection resistance, or replace human threat modeling.

## Workflow controls checked

- Explicit provider, model identifier, and revision
- Tool allowlists
- Input validation and prompt-injection screening declarations
- Output schema declaration
- PII handling policy
- Human approval for high-risk workflows
- Per-run spend caps and bounded iterations
- Secret redaction in telemetry

## Deployment defaults

The container runs as a non-root UID, exposes only the HTTP API port, disables privilege escalation, drops Linux capabilities, and uses a read-only root filesystem in the Helm example. The service does not persist submitted workflow documents and suppresses request-body logging.

These controls are examples to adapt and review. The Terraform folders are plans/templates for private object-storage buckets and must be reviewed for account policy, residency, IAM, encryption, retention, networking, and estimated cost before any apply.