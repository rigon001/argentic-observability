# ARGENTIC Observability

Observability and benchmarking infrastructure for local and distributed agentic AI deployments developed by the University of Maribor within the ARGENTIC project.

The project currently provides a reproducible Prometheus and Grafana deployment and will progressively integrate host, container, model-server, GPU, agent, tracing, and benchmarking telemetry.

## Purpose

The platform is intended to support:

- monitoring of local AI inference services;
- comparison of vLLM and llama.cpp deployments;
- host, container, GPU, and application telemetry;
- correlation of infrastructure metrics with Basic Agent requests;
- reproducible performance and energy benchmarks;
- future robustness, efficiency, provenance, and compliance evaluation.

The work supports UM activities related to distributed Edge-Cloud-HPC agents and the WP6 evaluation and lifecycle framework.

## Current architecture

```text
DGX Spark host
  |
  +-- Node Exporter --> host CPU, memory, disk and network
  |
  +-- cAdvisor ------> per-container CPU, memory, disk and network
  |
  v
Prometheus
  |
  v
Grafana

## Current collectors

| Component | Scope | Port |
|---|---|---:|
| Prometheus | Metrics collection and storage | 9090 |
| Grafana | Queries and visualisation | 3000 |
| Node Exporter | DGX Spark host metrics | 9100 |
| cAdvisor | Docker container metrics | 8080 |

## Planned development

- [x] Prometheus and Grafana
- [x] Node Exporter for host metrics
- [x] cAdvisor for container metrics
- [ ] Native vLLM metrics
- [ ] Native llama.cpp metrics
- [ ] DGX Spark GPU telemetry through DCGM or NVML
- [ ] OpenTelemetry instrumentation for Basic Agent
- [ ] Correlation of OpenTelemetry trace IDs and Basic Agent JSON traces
- [ ] Reproducible benchmark runner and results schema
- [ ] Controlled vLLM versus llama.cpp comparison
- [ ] MLflow integration