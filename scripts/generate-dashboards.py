#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("grafana/dashboards")

DATASOURCE = {
    "type": "prometheus",
    "uid": "prometheus",
}


def target(
    expr: str,
    legend: str,
    ref_id: str = "A",
    instant: bool = False,
) -> dict[str, Any]:
    return {
        "datasource": DATASOURCE,
        "editorMode": "code",
        "expr": expr,
        "legendFormat": legend,
        "range": not instant,
        "instant": instant,
        "refId": ref_id,
    }


def grid(x: int, y: int, w: int, h: int) -> dict[str, int]:
    return {"x": x, "y": y, "w": w, "h": h}


def time_series(
    title: str,
    x: int,
    y: int,
    w: int,
    h: int,
    targets: list[dict[str, Any]],
    unit: str = "short",
    minimum: float | None = None,
    maximum: float | None = None,
) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "color": {"mode": "palette-classic"},
        "custom": {
            "axisCenteredZero": False,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "drawStyle": "line",
            "fillOpacity": 12,
            "gradientMode": "none",
            "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False,
            },
            "lineInterpolation": "linear",
            "lineWidth": 2,
            "pointSize": 3,
            "scaleDistribution": {"type": "linear"},
            "showPoints": "never",
            "spanNulls": False,
            "stacking": {
                "group": "A",
                "mode": "none",
            },
            "thresholdsStyle": {"mode": "off"},
        },
        "mappings": [],
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "green", "value": None},
                {"color": "red", "value": 80},
            ],
        },
        "unit": unit,
    }

    if minimum is not None:
        defaults["min"] = minimum

    if maximum is not None:
        defaults["max"] = maximum

    return {
        "type": "timeseries",
        "title": title,
        "datasource": DATASOURCE,
        "gridPos": grid(x, y, w, h),
        "fieldConfig": {
            "defaults": defaults,
            "overrides": [],
        },
        "options": {
            "legend": {
                "calcs": [],
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": True,
            },
            "tooltip": {
                "hideZeros": False,
                "mode": "multi",
                "sort": "desc",
            },
        },
        "targets": targets,
    }


def stat(
    title: str,
    x: int,
    y: int,
    w: int,
    h: int,
    targets: list[dict[str, Any]],
    unit: str = "short",
    health_mapping: bool = False,
) -> dict[str, Any]:
    mappings: list[dict[str, Any]] = []

    if health_mapping:
        mappings = [
            {
                "options": {
                    "0": {
                        "color": "red",
                        "index": 0,
                        "text": "DOWN",
                    },
                    "1": {
                        "color": "green",
                        "index": 1,
                        "text": "UP",
                    },
                },
                "type": "value",
            }
        ]

    return {
        "type": "stat",
        "title": title,
        "datasource": DATASOURCE,
        "gridPos": grid(x, y, w, h),
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "thresholds"},
                "mappings": mappings,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "red", "value": None},
                        {"color": "green", "value": 1},
                    ],
                },
                "unit": unit,
            },
            "overrides": [],
        },
        "options": {
            "colorMode": "background",
            "graphMode": "area",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False,
            },
            "showPercentChange": False,
            "textMode": "auto",
            "wideLayout": True,
        },
        "targets": targets,
    }


def dashboard(
    uid: str,
    title: str,
    panels: list[dict[str, Any]],
    tags: list[str],
) -> dict[str, Any]:
    return {
        "id": None,
        "uid": uid,
        "title": title,
        "tags": tags,
        "timezone": "browser",
        "editable": True,
        "graphTooltip": 1,
        "panels": panels,
        "time": {
            "from": "now-1h",
            "to": "now",
        },
        "timepicker": {
            "refresh_intervals": [
                "5s",
                "10s",
                "30s",
                "1m",
                "5m",
            ]
        },
        "templating": {"list": []},
        "annotations": {"list": []},
        "refresh": "5s",
        "schemaVersion": 41,
        "version": 1,
        "links": [],
    }


def system_overview() -> dict[str, Any]:
    panels = [
        stat(
            "Target health",
            0, 0, 12, 4,
            [
                target(
                    'up{job=~"prometheus|node-exporter|cadvisor|vllm"}',
                    "{{job}}",
                    instant=True,
                )
            ],
            health_mapping=True,
        ),
        stat(
            "vLLM target",
            12, 0, 4, 4,
            [target('up{job="vllm"}', "vLLM", instant=True)],
            health_mapping=True,
        ),
        stat(
            "Running requests",
            16, 0, 4, 4,
            [
                target(
                    'sum(vllm:num_requests_running{job="vllm"})',
                    "Running",
                    instant=True,
                )
            ],
        ),
        stat(
            "Waiting requests",
            20, 0, 4, 4,
            [
                target(
                    'sum(vllm:num_requests_waiting{job="vllm"})',
                    "Waiting",
                    instant=True,
                )
            ],
        ),
        time_series(
            "Host CPU usage",
            0, 4, 8, 8,
            [
                target(
                    """
100 * (
  1 -
  avg by (instance) (
    rate(node_cpu_seconds_total{
      job="node-exporter",
      mode="idle"
    }[5m])
  )
)
""".strip(),
                    "CPU",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "Host memory usage",
            8, 4, 8, 8,
            [
                target(
                    """
100 * (
  1 -
  node_memory_MemAvailable_bytes{job="node-exporter"}
  /
  node_memory_MemTotal_bytes{job="node-exporter"}
)
""".strip(),
                    "Memory",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "vLLM token throughput",
            16, 4, 8, 8,
            [
                target(
                    """
sum(
  rate(vllm:prompt_tokens_total{job="vllm"}[5m])
)
""".strip(),
                    "Prompt tokens/s",
                    "A",
                ),
                target(
                    """
sum(
  rate(vllm:generation_tokens_total{job="vllm"}[5m])
)
""".strip(),
                    "Generated tokens/s",
                    "B",
                ),
            ],
            unit="ops",
            minimum=0,
        ),
        time_series(
            "Top container CPU usage",
            0, 12, 12, 9,
            [
                target(
                    """
topk(
  10,
  100 * sum by (name) (
    rate(container_cpu_usage_seconds_total{
      job="cadvisor",
      name!=""
    }[5m])
  )
)
""".strip(),
                    "{{name}}",
                )
            ],
            unit="percent",
            minimum=0,
        ),
        time_series(
            "Top container memory",
            12, 12, 12, 9,
            [
                target(
                    """
topk(
  10,
  sum by (name) (
    container_memory_working_set_bytes{
      job="cadvisor",
      name!=""
    }
  )
)
""".strip(),
                    "{{name}}",
                )
            ],
            unit="bytes",
            minimum=0,
        ),
        time_series(
            "vLLM requests",
            0, 21, 8, 8,
            [
                target(
                    'sum(vllm:num_requests_running{job="vllm"})',
                    "Running",
                    "A",
                ),
                target(
                    'sum(vllm:num_requests_waiting{job="vllm"})',
                    "Waiting",
                    "B",
                ),
            ],
            minimum=0,
        ),
        time_series(
            "vLLM p95 end-to-end latency",
            8, 21, 8, 8,
            [
                target(
                    """
histogram_quantile(
  0.95,
  sum by (le) (
    rate(
      vllm:e2e_request_latency_seconds_bucket{
        job="vllm"
      }[15m]
    )
  )
)
""".strip(),
                    "p95 latency",
                )
            ],
            unit="s",
            minimum=0,
        ),
        time_series(
            "vLLM KV-cache usage",
            16, 21, 8, 8,
            [
                target(
                    """
100 * (
  vllm:kv_cache_usage_perc{job="vllm"}
  or
  vllm:gpu_cache_usage_perc{job="vllm"}
)
""".strip(),
                    "{{model_name}}",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
    ]

    return dashboard(
        "argentic-system-overview",
        "ARGENTIC System Overview",
        panels,
        ["ARGENTIC", "UM", "overview"],
    )


def host_dashboard() -> dict[str, Any]:
    panels = [
        stat(
            "Node Exporter",
            0, 0, 6, 4,
            [target('up{job="node-exporter"}', "Host", instant=True)],
            health_mapping=True,
        ),
        stat(
            "Host uptime",
            6, 0, 6, 4,
            [
                target(
                    """
time() -
node_boot_time_seconds{job="node-exporter"}
""".strip(),
                    "Uptime",
                    instant=True,
                )
            ],
            unit="s",
        ),
        stat(
            "Logical CPUs",
            12, 0, 6, 4,
            [
                target(
                    """
count(
  node_cpu_seconds_total{
    job="node-exporter",
    mode="idle"
  }
)
""".strip(),
                    "CPUs",
                    instant=True,
                )
            ],
        ),
        stat(
            "Total memory",
            18, 0, 6, 4,
            [
                target(
                    'node_memory_MemTotal_bytes{job="node-exporter"}',
                    "Memory",
                    instant=True,
                )
            ],
            unit="bytes",
        ),
        time_series(
            "Total CPU usage",
            0, 4, 12, 8,
            [
                target(
                    """
100 * (
  1 -
  avg by (instance) (
    rate(node_cpu_seconds_total{
      job="node-exporter",
      mode="idle"
    }[5m])
  )
)
""".strip(),
                    "CPU",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "CPU usage by core",
            12, 4, 12, 8,
            [
                target(
                    """
100 * (
  1 -
  avg by (cpu) (
    rate(node_cpu_seconds_total{
      job="node-exporter",
      mode="idle"
    }[5m])
  )
)
""".strip(),
                    "CPU {{cpu}}",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "Memory usage",
            0, 12, 12, 8,
            [
                target(
                    """
100 * (
  1 -
  node_memory_MemAvailable_bytes{job="node-exporter"}
  /
  node_memory_MemTotal_bytes{job="node-exporter"}
)
""".strip(),
                    "Memory",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "Load average",
            12, 12, 12, 8,
            [
                target(
                    'node_load1{job="node-exporter"}',
                    "1 minute",
                    "A",
                ),
                target(
                    'node_load5{job="node-exporter"}',
                    "5 minutes",
                    "B",
                ),
                target(
                    'node_load15{job="node-exporter"}',
                    "15 minutes",
                    "C",
                ),
            ],
            minimum=0,
        ),
        time_series(
            "Filesystem usage",
            0, 20, 12, 9,
            [
                target(
                    """
100 * (
  1 -
  node_filesystem_avail_bytes{
    job="node-exporter",
    fstype!~"tmpfs|devtmpfs|overlay|squashfs"
  }
  /
  node_filesystem_size_bytes{
    job="node-exporter",
    fstype!~"tmpfs|devtmpfs|overlay|squashfs"
  }
)
""".strip(),
                    "{{mountpoint}}",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "Disk throughput",
            12, 20, 12, 9,
            [
                target(
                    """
sum by (device) (
  rate(node_disk_read_bytes_total{
    job="node-exporter",
    device!~"loop.*|ram.*"
  }[5m])
)
""".strip(),
                    "{{device}} read",
                    "A",
                ),
                target(
                    """
sum by (device) (
  rate(node_disk_written_bytes_total{
    job="node-exporter",
    device!~"loop.*|ram.*"
  }[5m])
)
""".strip(),
                    "{{device}} write",
                    "B",
                ),
            ],
            unit="Bps",
            minimum=0,
        ),
        time_series(
            "Network throughput",
            0, 29, 12, 9,
            [
                target(
                    """
sum by (device) (
  rate(node_network_receive_bytes_total{
    job="node-exporter",
    device!="lo"
  }[5m])
)
""".strip(),
                    "{{device}} receive",
                    "A",
                ),
                target(
                    """
sum by (device) (
  rate(node_network_transmit_bytes_total{
    job="node-exporter",
    device!="lo"
  }[5m])
)
""".strip(),
                    "{{device}} transmit",
                    "B",
                ),
            ],
            unit="Bps",
            minimum=0,
        ),
        time_series(
            "Host temperature sensors",
            12, 29, 12, 9,
            [
                target(
                    'node_hwmon_temp_celsius{job="node-exporter"}',
                    "{{chip}} {{sensor}}",
                )
            ],
            unit="celsius",
        ),
    ]

    return dashboard(
        "dgx-spark-host",
        "DGX Spark Host",
        panels,
        ["ARGENTIC", "UM", "DGX Spark", "host"],
    )


def vllm_dashboard() -> dict[str, Any]:
    panels = [
        stat(
            "vLLM target",
            0, 0, 6, 4,
            [target('up{job="vllm"}', "vLLM", instant=True)],
            health_mapping=True,
        ),
        stat(
            "Running requests",
            6, 0, 6, 4,
            [
                target(
                    'sum(vllm:num_requests_running{job="vllm"})',
                    "Running",
                    instant=True,
                )
            ],
        ),
        stat(
            "Waiting requests",
            12, 0, 6, 4,
            [
                target(
                    'sum(vllm:num_requests_waiting{job="vllm"})',
                    "Waiting",
                    instant=True,
                )
            ],
        ),
        stat(
            "KV-cache usage",
            18, 0, 6, 4,
            [
                target(
                    """
100 * (
  vllm:kv_cache_usage_perc{job="vllm"}
  or
  vllm:gpu_cache_usage_perc{job="vllm"}
)
""".strip(),
                    "{{model_name}}",
                    instant=True,
                )
            ],
            unit="percent",
        ),
        time_series(
            "Running and waiting requests",
            0, 4, 12, 8,
            [
                target(
                    'sum(vllm:num_requests_running{job="vllm"})',
                    "Running",
                    "A",
                ),
                target(
                    'sum(vllm:num_requests_waiting{job="vllm"})',
                    "Waiting",
                    "B",
                ),
            ],
            minimum=0,
        ),
        time_series(
            "Successful requests per second",
            12, 4, 12, 8,
            [
                target(
                    """
sum by (model_name) (
  rate(vllm:request_success_total{
    job="vllm"
  }[5m])
)
""".strip(),
                    "{{model_name}}",
                )
            ],
            unit="reqps",
            minimum=0,
        ),
        time_series(
            "Token throughput",
            0, 12, 12, 8,
            [
                target(
                    """
sum by (model_name) (
  rate(vllm:prompt_tokens_total{
    job="vllm"
  }[5m])
)
""".strip(),
                    "{{model_name}} prompt",
                    "A",
                ),
                target(
                    """
sum by (model_name) (
  rate(vllm:generation_tokens_total{
    job="vllm"
  }[5m])
)
""".strip(),
                    "{{model_name}} generated",
                    "B",
                ),
            ],
            unit="ops",
            minimum=0,
        ),
        time_series(
            "KV-cache usage",
            12, 12, 12, 8,
            [
                target(
                    """
100 * (
  vllm:kv_cache_usage_perc{job="vllm"}
  or
  vllm:gpu_cache_usage_perc{job="vllm"}
)
""".strip(),
                    "{{model_name}}",
                )
            ],
            unit="percent",
            minimum=0,
            maximum=100,
        ),
        time_series(
            "Time to first token",
            0, 20, 12, 8,
            [
                target(
                    """
histogram_quantile(
  0.50,
  sum by (le, model_name) (
    rate(
      vllm:time_to_first_token_seconds_bucket{
        job="vllm"
      }[15m]
    )
  )
)
""".strip(),
                    "{{model_name}} p50",
                    "A",
                ),
                target(
                    """
histogram_quantile(
  0.95,
  sum by (le, model_name) (
    rate(
      vllm:time_to_first_token_seconds_bucket{
        job="vllm"
      }[15m]
    )
  )
)
""".strip(),
                    "{{model_name}} p95",
                    "B",
                ),
            ],
            unit="s",
            minimum=0,
        ),
        time_series(
            "End-to-end request latency",
            12, 20, 12, 8,
            [
                target(
                    """
sum by (model_name) (
  rate(
    vllm:e2e_request_latency_seconds_sum{
      job="vllm"
    }[15m]
  )
)
/
sum by (model_name) (
  rate(
    vllm:e2e_request_latency_seconds_count{
      job="vllm"
    }[15m]
  )
)
""".strip(),
                    "{{model_name}} average",
                    "A",
                ),
                target(
                    """
histogram_quantile(
  0.95,
  sum by (le, model_name) (
    rate(
      vllm:e2e_request_latency_seconds_bucket{
        job="vllm"
      }[15m]
    )
  )
)
""".strip(),
                    "{{model_name}} p95",
                    "B",
                ),
            ],
            unit="s",
            minimum=0,
        ),
        time_series(
            "p95 queue time",
            0, 28, 8, 8,
            [
                target(
                    """
histogram_quantile(
  0.95,
  sum by (le, model_name) (
    rate(
      vllm:request_queue_time_seconds_bucket{
        job="vllm"
      }[15m]
    )
  )
)
""".strip(),
                    "{{model_name}}",
                )
            ],
            unit="s",
            minimum=0,
        ),
        time_series(
            "Preemptions",
            8, 28, 8, 8,
            [
                target(
                    """
sum by (model_name) (
  increase(
    vllm:num_preemptions_total{
      job="vllm"
    }[15m]
  )
)
""".strip(),
                    "{{model_name}}",
                )
            ],
            minimum=0,
        ),
        time_series(
            "vLLM container CPU",
            16, 28, 8, 8,
            [
                target(
                    """
100 *
sum by (name) (
  rate(
    container_cpu_usage_seconds_total{
      job="cadvisor",
      name=~".*vllm.*"
    }[5m]
  )
)
""".strip(),
                    "{{name}}",
                )
            ],
            unit="percent",
            minimum=0,
        ),
        time_series(
            "vLLM container memory",
            0, 36, 12, 8,
            [
                target(
                    """
sum by (name) (
  container_memory_working_set_bytes{
    job="cadvisor",
    name=~".*vllm.*"
  }
)
""".strip(),
                    "{{name}}",
                )
            ],
            unit="bytes",
            minimum=0,
        ),
        time_series(
            "Prompt cache activity",
            12, 36, 12, 8,
            [
                target(
                    """
sum by (model_name) (
  rate(
    vllm:prompt_tokens_cached_total{
      job="vllm"
    }[5m]
  )
)
""".strip(),
                    "{{model_name}} cached tokens/s",
                )
            ],
            unit="ops",
            minimum=0,
        ),
    ]

    return dashboard(
        "vllm-inference",
        "vLLM Inference",
        panels,
        ["ARGENTIC", "UM", "vLLM", "inference"],
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dashboards = {
        "argentic-system-overview.json": system_overview(),
        "dgx-spark-host.json": host_dashboard(),
        "vllm-inference.json": vllm_dashboard(),
    }

    for filename, data in dashboards.items():
        path = OUTPUT_DIR / filename
        path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Created {path}")


if __name__ == "__main__":
    main()
