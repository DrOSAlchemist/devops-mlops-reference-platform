# Structured logs and ELK

The `/scan` endpoint emits one JSON event to stdout after evaluation. It contains the event name, finding count, blocked status, and severities only; submitted YAML, prompt text, headers, and tool payloads are never written to logs.

`observability/elk/logstash.conf` is an example Logstash TCP/JSON-lines input for a cluster-local log forwarder. Restrict the listener to trusted cluster traffic, add TLS/authentication for cross-network use, and retain only the fields needed for operations. The filter drops common secret-bearing fields as defense in depth; redaction at the application boundary remains the primary control.

For Prometheus and Grafana, use `observability/prometheus/prometheus.yml`, `alerts.yml`, and `observability/grafana/platform-guard-overview.json`. Set alert thresholds from service objectives and measured baselines rather than treating the starter rules as production SLOs.