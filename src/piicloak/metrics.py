"""
Prometheus metrics for monitoring.
"""

import time
from functools import wraps
from flask import request, g


# Simple in-memory metrics (for production, use prometheus_client)
class Metrics:
    def __init__(self):
        self.requests_total = 0
        self.requests_by_endpoint = {}
        self.request_duration_seconds = []
        self.errors_total = 0
        self.pii_entities_detected = 0
    
    def record_request(self, endpoint):
        self.requests_total += 1
        self.requests_by_endpoint[endpoint] = self.requests_by_endpoint.get(endpoint, 0) + 1
    
    def record_duration(self, duration):
        self.request_duration_seconds.append(duration)
        # Keep only last 1000 measurements
        if len(self.request_duration_seconds) > 1000:
            self.request_duration_seconds = self.request_duration_seconds[-1000:]
    
    def record_error(self):
        self.errors_total += 1
    
    def record_entities(self, count):
        self.pii_entities_detected += count
    
    def get_metrics(self):
        """Return metrics in Prometheus format."""
        avg_duration = sum(self.request_duration_seconds) / len(self.request_duration_seconds) if self.request_duration_seconds else 0
        
        lines = [
            "# HELP piicloak_requests_total Total number of HTTP requests",
            "# TYPE piicloak_requests_total counter",
            f"piicloak_requests_total {self.requests_total}",
            "",
            "# HELP piicloak_errors_total Total number of errors",
            "# TYPE piicloak_errors_total counter",
            f"piicloak_errors_total {self.errors_total}",
            "",
            "# HELP piicloak_entities_detected_total Total PII entities detected",
            "# TYPE piicloak_entities_detected_total counter",
            f"piicloak_entities_detected_total {self.pii_entities_detected}",
            "",
            "# HELP piicloak_request_duration_seconds Average request duration",
            "# TYPE piicloak_request_duration_seconds gauge",
            f"piicloak_request_duration_seconds {avg_duration:.4f}",
            "",
        ]
        
        # Add per-endpoint metrics
        lines.append("# HELP piicloak_requests_by_endpoint Requests by endpoint")
        lines.append("# TYPE piicloak_requests_by_endpoint counter")
        for endpoint, count in self.requests_by_endpoint.items():
            lines.append(f'piicloak_requests_by_endpoint{{endpoint="{endpoint}"}} {count}')
        
        return "\n".join(lines)


# Global metrics instance
metrics = Metrics()


def setup_metrics(app):
    """Configure metrics collection."""
    
    @app.before_request
    def start_timer():
        g.start_time = time.time()
    
    @app.after_request
    def record_metrics(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            metrics.record_duration(duration)
            metrics.record_request(request.endpoint or request.path)
            
            if response.status_code >= 400:
                metrics.record_error()
        
        return response


def track_entities(count):
    """Track number of PII entities detected."""
    metrics.record_entities(count)
