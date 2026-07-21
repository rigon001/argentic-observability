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
Browser
  |
  +-- localhost:3000 --> Grafana
  |
  +-- localhost:9090 --> Prometheus

Grafana
  |
  +-- queries Prometheus

Prometheus
  |
  +-- currently scrapes Prometheus itself