from __future__ import annotations

import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import yaml

from platform_guard.scanner import scan_workflow

_scan_requests = 0
_finding_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
_logger = logging.getLogger("platform_guard")
_logger.setLevel(logging.INFO)


class GuardHandler(BaseHTTPRequestHandler):
    server_version = "PlatformGuard/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path == "/metrics":
            lines = ["# TYPE platform_guard_scan_requests_total counter"]
            lines.append(f"platform_guard_scan_requests_total {_scan_requests}")
            lines.append("# TYPE platform_guard_findings_total counter")
            for severity, count in _finding_counts.items():
                lines.append(f'platform_guard_findings_total{{severity="{severity}"}} {count}')
            body = "\n".join(lines) + "\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        global _scan_requests
        if self.path != "/scan":
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return
        if content_length <= 0 or content_length > 1_000_000:
            self._send_json(413, {"error": "request_size_invalid"})
            return

        try:
            document: Any = yaml.safe_load(self.rfile.read(content_length))
        except yaml.YAMLError:
            self._send_json(400, {"error": "invalid_yaml"})
            return

        findings = scan_workflow(document)
        _scan_requests += 1
        for finding in findings:
            severity = finding["severity"]
            _finding_counts[severity] = _finding_counts.get(severity, 0) + 1
        if not logging.getLogger().handlers:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        _logger.info(
            json.dumps(
                {
                    "event": "workflow_scan",
                    "finding_count": len(findings),
                    "blocked": any(item["severity"] in {"critical", "high"} for item in findings),
                    "severities": sorted({item["severity"] for item in findings}),
                },
                sort_keys=True,
            )
        )
        self._send_json(200, {"passed": not findings, "finding_count": len(findings), "findings": findings})

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), GuardHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()