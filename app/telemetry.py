import logging
import sys
from prometheus_client import Counter

# Metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP Requests", 
    ["method", "endpoint", "http_status"]
)

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        format='{"time":"%(asctime)s", "level":"%(levelname)s", "msg":"%(message)s"}',
        level=logging.INFO
    )

async def metrics_middleware(request, call_next):
    method = request.method
    path = request.url.path
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=method, 
        endpoint=path, 
        http_status=response.status_code
    ).inc()
    
    return response