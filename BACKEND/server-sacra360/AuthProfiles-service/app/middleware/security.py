"""
Middleware de seguridad
Rate limiting y security headers
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Almacenamiento en memoria de requests (en producción usar Redis)
request_counts = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting
    Limita el número de requests por IP en un período de tiempo
    """
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host
        
        # Excluir health check del rate limiting
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Limpiar requests antiguos
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if req_time > cutoff
        ]
        
        # Verificar límite
        if len(request_counts[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Demasiadas solicitudes. Límite: {self.max_requests} por {self.window_seconds} segundos"
                }
            )
        
        # Registrar request
        request_counts[client_ip].append(now)
        
        # Continuar con la request
        response = await call_next(request)
        
        # Agregar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(request_counts[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.window_seconds)).timestamp())
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para agregar security headers
    Protege contra ataques comunes
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
