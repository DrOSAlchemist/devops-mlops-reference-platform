import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

import yaml

from platform_guard.server import GuardHandler


def test_health_and_scan_endpoints(caplog):
    server = ThreadingHTTPServer(("127.0.0.1", 0), GuardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"

    try:
        with urlopen(base_url + "/health", timeout=2) as response:
            assert response.status == 200
            assert json.loads(response.read()) == {"status": "ok"}

        workflow = {
            "workflow": {
                "risk": "high",
                "model": {"provider": "test", "id": "model", "revision": "v1"},
                "tools": {"allowed": ["read_docs"]},
                "input": {"validation": True, "prompt_injection_screening": True},
                "output": {"schema": "response-v1"},
                "data": {"pii_handling": "redact", "test_marker": "DO_NOT_LOG_ME"},
                "governance": {"human_approval_required": True},
                "budget": {"max_usd": 1.0},
                "limits": {"max_steps": 5},
                "observability": {"redact_secrets": True},
            }
        }
        request = Request(
            base_url + "/scan",
            data=yaml.safe_dump(workflow).encode("utf-8"),
            headers={"Content-Type": "application/yaml"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            result = json.loads(response.read())
            assert response.status == 200
            assert result == {"passed": True, "finding_count": 0, "findings": []}

        with urlopen(base_url + "/metrics", timeout=2) as response:
            metrics = response.read().decode("utf-8")
            assert "platform_guard_scan_requests_total" in metrics

        assert '"event": "workflow_scan"' in caplog.text
        assert "DO_NOT_LOG_ME" not in caplog.text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)