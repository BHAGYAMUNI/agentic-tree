Observability and Logging

This project includes basic logging configuration. Suggested next steps:

- Use structured logging (structlog or json logging) for production.
- Integrate a log aggregation/monitoring service (Datadog, Sentry, ELK).
- Expose Prometheus metrics using `prometheus_client` and instrument key endpoints.

Quick start (local):

- Logs are emitted to stdout by default via `logging` module.
- To add Prometheus metrics:

```bash
pip install prometheus_client
```

Then add a `/metrics` endpoint exporting metrics.
