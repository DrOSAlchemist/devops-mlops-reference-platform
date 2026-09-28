from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_workflow(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as workflow_file:
        return yaml.safe_load(workflow_file)


def _finding(rule_id: str, severity: str, path: str, message: str, remediation: str) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "path": path,
        "message": message,
        "remediation": remediation,
    }


def scan_workflow(document: Any) -> list[dict[str, str]]:
    """Return deterministic findings for missing AI workflow guardrails."""
    findings: list[dict[str, str]] = []
    if not isinstance(document, dict):
        return [
            _finding(
                "CFG001",
                "critical",
                "$",
                "Workflow configuration must be a YAML mapping.",
                "Provide a mapping with model, tools, input, output, and governance sections.",
            )
        ]

    workflow = document.get("workflow", document)
    if not isinstance(workflow, dict):
        return [
            _finding(
                "CFG001",
                "critical",
                "workflow",
                "The workflow field must be a YAML mapping.",
                "Replace the workflow value with a mapping of workflow settings.",
            )
        ]

    model = workflow.get("model")
    if not isinstance(model, dict) or not all(
        isinstance(model.get(field), str) and model[field].strip()
        for field in ("provider", "id", "revision")
    ):
        findings.append(
            _finding(
                "MOD001",
                "high",
                "workflow.model",
                "Model provider, identifier, and revision must be explicit.",
                "Pin the provider, model ID, and immutable model revision for reproducible releases.",
            )
        )

    tools = workflow.get("tools")
    allowed_tools = tools.get("allowed") if isinstance(tools, dict) else None
    if not isinstance(allowed_tools, list) or not allowed_tools or not all(
        isinstance(tool, str) and tool.strip() for tool in allowed_tools
    ):
        findings.append(
            _finding(
                "TOOL001",
                "high",
                "workflow.tools.allowed",
                "An explicit non-empty tool allowlist is required.",
                "List only the tools this workflow needs; do not grant ambient tool access.",
            )
        )

    input_policy = workflow.get("input")
    if not isinstance(input_policy, dict) or input_policy.get("validation") is not True:
        findings.append(
            _finding(
                "INP001",
                "high",
                "workflow.input.validation",
                "Input validation is not enabled.",
                "Validate input shape and size before the model or tools receive it.",
            )
        )
    if not isinstance(input_policy, dict) or input_policy.get("prompt_injection_screening") is not True:
        findings.append(
            _finding(
                "INP002",
                "high",
                "workflow.input.prompt_injection_screening",
                "Prompt-injection screening is not enabled.",
                "Screen user input and retrieved content before tool execution.",
            )
        )

    output_policy = workflow.get("output")
    if not isinstance(output_policy, dict) or not (
        isinstance(output_policy.get("schema"), str) and output_policy["schema"].strip()
    ):
        findings.append(
            _finding(
                "OUT001",
                "medium",
                "workflow.output.schema",
                "A validated output schema is not configured.",
                "Define the expected output shape and validate model responses before use.",
            )
        )

    data_policy = workflow.get("data")
    pii_handling = data_policy.get("pii_handling") if isinstance(data_policy, dict) else None
    if not isinstance(pii_handling, str) or pii_handling not in {"redact", "deny"}:
        findings.append(
            _finding(
                "DAT001",
                "high",
                "workflow.data.pii_handling",
                "A restrictive PII handling policy is not configured.",
                "Choose either redact or deny before sensitive data enters model context.",
            )
        )

    governance = workflow.get("governance")
    risk = workflow.get("risk", "high")
    if not isinstance(risk, str) or risk not in {"low", "medium", "high", "critical"}:
        findings.append(
            _finding(
                "GOV002",
                "high",
                "workflow.risk",
                "Workflow risk must be low, medium, high, or critical.",
                "Declare the risk level; unknown values are treated as high risk.",
            )
        )
        risk = "high"
    if risk in {"high", "critical"} and (
        not isinstance(governance, dict) or governance.get("human_approval_required") is not True
    ):
        findings.append(
            _finding(
                "GOV001",
                "high",
                "workflow.governance.human_approval_required",
                "High-risk workflows must require human approval.",
                "Require an approval step before consequential or external actions.",
            )
        )

    budget = workflow.get("budget")
    max_cost = budget.get("max_usd") if isinstance(budget, dict) else None
    if isinstance(max_cost, bool) or not isinstance(max_cost, (int, float)) or max_cost <= 0:
        findings.append(
            _finding(
                "BUD001",
                "medium",
                "workflow.budget.max_usd",
                "A positive per-run cost limit is not configured.",
                "Set a maximum spend for model and tool use in each workflow run.",
            )
        )

    limits = workflow.get("limits")
    max_steps = limits.get("max_steps") if isinstance(limits, dict) else None
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 20:
        findings.append(
            _finding(
                "LIM001",
                "medium",
                "workflow.limits.max_steps",
                "Workflow iteration count is unbounded or outside the supported range.",
                "Set max_steps to an integer from 1 through 20.",
            )
        )

    observability = workflow.get("observability")
    if not isinstance(observability, dict) or observability.get("redact_secrets") is not True:
        findings.append(
            _finding(
                "OBS001",
                "high",
                "workflow.observability.redact_secrets",
                "Secret redaction is not enabled for workflow telemetry.",
                "Redact credentials and sensitive values before logging prompts, tool calls, or outputs.",
            )
        )

    return findings


def is_blocking(findings: list[dict[str, str]]) -> bool:
    return any(finding["severity"] in {"critical", "high"} for finding in findings)