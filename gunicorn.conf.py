"""
Gunicorn configuration for PIICloak production deployment.
"""

import os
import multiprocessing

# Server socket
bind = f"{os.getenv('PIICLOAK_HOST', '0.0.0.0')}:{os.getenv('PIICLOAK_PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('PIICLOAK_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('PIICLOAK_LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'piicloak'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
