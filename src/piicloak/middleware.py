"""
Middleware for authentication, CORS, logging, and security.
"""

import time
import uuid
import logging
from functools import wraps
from flask import request, jsonify, g
from .config import API_KEY, CORS_ORIGINS


def setup_middleware(app):
    """Configure all middleware for the Flask app."""
    setup_logging(app)
    setup_cors(app)
    setup_security_headers(app)
    setup_request_id(app)
    
    if API_KEY:
        setup_auth(app)


def setup_logging(app):
    """Configure structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    @app.before_request
    def log_request():
        g.start_time = time.time()
        app.logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(
                f"Response: {request.method} {request.path} "
                f"Status={response.status_code} Duration={duration:.3f}s"
            )
        return response


def setup_cors(app):
    """Configure CORS headers."""
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = CORS_ORIGINS
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response


def setup_security_headers(app):
    """Add security headers to all responses."""
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response


def setup_request_id(app):
    """Add request ID for tracing."""
    @app.before_request
    def add_request_id():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    @app.after_request
    def add_request_id_header(response):
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response


def setup_auth(app):
    """Configure API key authentication if enabled."""
    @app.before_request
    def check_auth():
        # Skip auth for health and metrics endpoints
        if request.path in ['/health', '/metrics', '/entities']:
            return
        
        # Check API key
        auth_header = request.headers.get('Authorization', '')
        api_key = auth_header.replace('Bearer ', '').replace('ApiKey ', '')
        
        if api_key != API_KEY:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid API key required"
            }), 401


def require_auth(f):
    """Decorator to require authentication for specific endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEY:
            auth_header = request.headers.get('Authorization', '')
            api_key = auth_header.replace('Bearer ', '').replace('ApiKey ', '')
            
            if api_key != API_KEY:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Valid API key required"
                }), 401
        
        return f(*args, **kwargs)
    return decorated_function
