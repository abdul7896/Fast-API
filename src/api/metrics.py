"""
Metrics module for Prima API
Provides Prometheus-compatible metrics endpoint
"""

import time
from typing import Dict, Any
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# Simple in-memory metrics store
_metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_by_endpoint": {},
    "response_time_seconds": [],
    "errors_total": 0,
    "uptime_start": time.time()
}

router = APIRouter()


def increment_requests(endpoint: str = "unknown"):
    """Increment request counter for an endpoint"""
    _metrics["requests_total"] += 1
    if endpoint not in _metrics["requests_by_endpoint"]:
        _metrics["requests_by_endpoint"][endpoint] = 0
    _metrics["requests_by_endpoint"][endpoint] += 1


def record_response_time(duration: float):
    """Record response time in seconds"""
    _metrics["response_time_seconds"].append(duration)
    # Keep only last 1000 measurements
    if len(_metrics["response_time_seconds"]) > 1000:
        _metrics["response_time_seconds"] = _metrics["response_time_seconds"][-1000:]


def increment_errors():
    """Increment error counter"""
    _metrics["errors_total"] += 1


@router.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
async def metrics_endpoint():
    """
    Prometheus-compatible metrics endpoint
    
    Returns:
        Plain text metrics in Prometheus format
    """
    uptime = time.time() - _metrics["uptime_start"]
    avg_response_time = (
        sum(_metrics["response_time_seconds"]) / len(_metrics["response_time_seconds"])
        if _metrics["response_time_seconds"]
        else 0
    )
    
    metrics_text = f"""# HELP prima_api_requests_total Total number of HTTP requests
# TYPE prima_api_requests_total counter
prima_api_requests_total {_metrics["requests_total"]}

# HELP prima_api_errors_total Total number of HTTP errors
# TYPE prima_api_errors_total counter
prima_api_errors_total {_metrics["errors_total"]}

# HELP prima_api_uptime_seconds Application uptime in seconds
# TYPE prima_api_uptime_seconds gauge
prima_api_uptime_seconds {uptime:.2f}

# HELP prima_api_response_time_seconds Average response time in seconds
# TYPE prima_api_response_time_seconds gauge
prima_api_response_time_seconds {avg_response_time:.4f}
"""

    # Add per-endpoint metrics
    for endpoint, count in _metrics["requests_by_endpoint"].items():
        metrics_text += f'prima_api_requests_by_endpoint{{endpoint="{endpoint}"}} {count}\n'

    return metrics_text
