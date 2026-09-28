# SLO and incident playbook

Use this checklist when adapting the sample service to an environment with real users. Values are examples to be agreed with the service owner; they are not measured claims about this repository.

## Starter service objectives

- Availability: define a monthly request-success target and exclude planned maintenance only if the service contract allows it.
- Latency: choose a p95 and p99 objective from observed client needs, not from a dashboard default.
- Policy evaluation: track scan volume, findings by severity, and scanner errors separately.
- AI workflow: measure model/tool latency, timeout rate, budget exhaustion, and human-approval wait time.

## Alert response

1. Page on a fast burn of the availability error budget or any new critical policy finding.
2. Route high findings to the service owner with the rule ID and remediation text.
3. Preserve correlation IDs and redacted metadata; never place raw credentials or unnecessary prompt data in telemetry.
4. Roll back the model or policy revision when a release gate fails; retain the evaluation result with the deployment revision.
5. Review alert noise and SLO fit after incidents and at regular service reviews.

The Prometheus alert examples cover critical/high policy findings. Add service-specific burn-rate alerts after collecting baseline traffic and latency data.