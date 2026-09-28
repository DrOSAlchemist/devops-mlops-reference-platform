from pathlib import Path

from platform_guard.scanner import is_blocking, load_workflow, scan_workflow


def test_guarded_workflow_passes():
    workflow = {
        "workflow": {
            "risk": "high",
            "model": {"provider": "azure-openai", "id": "model-a", "revision": "rev-1"},
            "tools": {"allowed": ["search_docs"]},
            "input": {"validation": True, "prompt_injection_screening": True},
            "output": {"schema": "response-v1"},
            "data": {"pii_handling": "redact"},
            "governance": {"human_approval_required": True},
            "budget": {"max_usd": 1.0},
            "limits": {"max_steps": 8},
            "observability": {"redact_secrets": True},
        }
    }

    assert scan_workflow(workflow) == []


def test_unguarded_workflow_reports_specific_findings():
    workflow = {
        "workflow": {
            "risk": "high",
            "model": {"provider": "openai", "id": "latest"},
            "tools": {"allowed": []},
            "input": {"validation": False, "prompt_injection_screening": False},
            "output": {},
            "data": {"pii_handling": "allow"},
            "governance": {"human_approval_required": False},
            "budget": {"max_usd": 0},
            "limits": {"max_steps": 0},
            "observability": {"redact_secrets": False},
        }
    }

    findings = scan_workflow(workflow)

    assert {finding["rule_id"] for finding in findings} == {
        "MOD001", "TOOL001", "INP001", "INP002", "OUT001", "DAT001",
        "GOV001", "BUD001", "LIM001", "OBS001",
    }
    assert is_blocking(findings)


def test_non_mapping_configuration_is_a_critical_finding():
    findings = scan_workflow(["not", "a", "mapping"])

    assert findings[0]["rule_id"] == "CFG001"
    assert is_blocking(findings)


def test_malformed_risk_and_data_values_do_not_crash():
    findings = scan_workflow({
        "workflow": {
            "risk": ["unexpected", "list"],
            "data": {"pii_handling": ["unexpected"]},
        }
    })

    assert "GOV002" in {finding["rule_id"] for finding in findings}
    assert "DAT001" in {finding["rule_id"] for finding in findings}


def test_guarded_provider_examples_pass():
    examples = Path(__file__).parents[1] / "examples" / "workflows"
    for filename in ("guarded-agent.yaml", "bedrock-agent.yaml", "vertex-agent.yaml"):
        assert scan_workflow(load_workflow(examples / filename)) == [], filename