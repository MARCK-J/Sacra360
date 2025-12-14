"""
Utilidades para AuthProfiles Service
Funciones auxiliares para autenticación y manejo de tokens
"""

from jose import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import secrets
import re
from passlib.context import CryptContext


# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT (en producción, usar variables de entorno)
SECRET_KEY = "tu-clave-secreta-muy-segura-cambia-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class PasswordUtils:
    """Utilidades para manejo de contraseñas"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseña usando bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """Generar contraseña aleatoria segura"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validar fortaleza de contraseña"""
        result = {
            "is_strong": True,
            "errors": [],
            "score": 0
        }
        
        # Longitud mínima
        if len(password) < 8:
            result["errors"].append("Debe tener al menos 8 caracteres")
            result["is_strong"] = False
        else:
            result["score"] += 1
        
        # Mayúsculas
        if not re.search(r'[A-Z]', password):
            result["errors"].append("Debe contener al menos una mayúscula")
            result["is_strong"] = False
        else:
            result["score"] += 1
        
        # Minúsculas
        if not re.search(r'[a-z]', password):
            result["errors"].append("Debe contener al menos una minúscula")
            result["is_strong"] = False
        else:
            result["score"] += 1
        
        # Números
        if not re.search(r'\d', password):
            result["errors"].append("Debe contener al menos un número")
            result["is_strong"] = False
        else:
            result["score"] += 1
        
        # Caracteres especiales
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["errors"].append("Debe contener al menos un carácter especial")
            result["is_strong"] = False
        else:
            result["score"] += 1
        
        return result


class JWTUtils:
    """Utilidades para manejo de tokens JWT"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Crear token de renovación"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens duran más
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    @staticmethod
    def extract_user_id(token: str) -> Optional[str]:
        """Extraer ID de usuario del token"""
        payload = JWTUtils.verify_token(token)
        if payload:
            return payload.get("sub")
        return None


class PermissionUtils:
    """Utilidades para manejo de permisos"""
    
    # Definición de permisos por rol
    ROLE_PERMISSIONS = {
        "archbishop": [
            "documents:*:*",           # Acceso total a documentos
            "users:*:*",              # Gestión total de usuarios
            "reports:*:*",            # Acceso total a reportes
            "sacraments:*:*",         # Acceso total a sacramentos
            "system:*:*"              # Acceso total al sistema
        ],
        "bishop": [
            "documents:*:read",       # Leer todos los documentos
            "documents:diocese:write", # Escribir en su diócesis
            "users:priest:manage",    # Gestionar sacerdotes
            "users:deacon:manage",    # Gestionar diáconos
            "reports:diocese:read",   # Reportes de su diócesis
            "sacraments:*:*"         # Todos los sacramentos
        ],
        "priest": [
            "documents:parish:read",  # Leer documentos de su parroquia
            "documents:parish:write", # Escribir en su parroquia
            "sacraments:baptism:*",   # Bautismos
            "sacraments:marriage:*",  # Matrimonios
            "sacraments:death:*",     # Defunciones
            "reports:parish:read"     # Reportes de su parroquia
        ],
        "deacon": [
            "documents:parish:read",  # Solo lectura en su parroquia
            "sacraments:baptism:read", # Solo leer bautismos
            "sacraments:marriage:assist" # Asistir en matrimonios
        ],
        "administrator": [
            "documents:*:read",       # Leer todos los documentos
            "documents:admin:write",  # Funciones administrativas
            "users:basic:read",       # Ver usuarios básicos
            "reports:admin:read"      # Reportes administrativos
        ],
        "archivist": [
            "documents:*:read",       # Leer todos los documentos
            "documents:archive:write", # Funciones de archivo
            "reports:archive:read"    # Reportes de archivo
        ],
        "viewer": [
            "documents:public:read"   # Solo documentos públicos
        ]
    }
    
    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """Obtener permisos por rol"""
        return PermissionUtils.ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def check_permission(user_permissions: List[str], required_permission: str) -> bool:
        """Verificar si el usuario tiene un permiso específico"""
        # Verificar permisos exactos
        if required_permission in user_permissions:
            return True
        
        # Verificar permisos con wildcards
        for permission in user_permissions:
            if PermissionUtils._match_wildcard_permission(permission, required_permission):
                return True
        
        return False
    
    @staticmethod
    def _match_wildcard_permission(permission_pattern: str, required_permission: str) -> bool:
        """Verificar coincidencia con wildcards"""
        pattern_parts = permission_pattern.split(':')
        required_parts = required_permission.split(':')
        
        if len(pattern_parts) != len(required_parts):
            return False
        
        for pattern_part, required_part in zip(pattern_parts, required_parts):
            if pattern_part != '*' and pattern_part != required_part:
                return False
        
        return True


class ValidationUtils:
    """Utilidades para validación de datos"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validar formato de teléfono colombiano"""
        # Formato: +57 XXX XXX XXXX o similares
        pattern = r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitizar entrada de usuario"""
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[<>"\']', '', input_str)
        return sanitized.strip()
    
    @staticmethod
    def validate_user_role(role: str) -> bool:
        """Validar que el rol existe"""
        valid_roles = ["archbishop", "bishop", "priest", "deacon", "administrator", "archivist", "viewer"]
        return role in valid_roles


class SecurityUtils:
    """Utilidades de seguridad"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generar ID de sesión único"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def is_request_rate_limited(user_id: str, max_requests: int = 100, window_minutes: int = 15) -> bool:
        """Verificar límite de velocidad de requests (implementación básica)"""
        # En producción, usar Redis o similar para tracking
        return False
    
    @staticmethod
    def log_security_event(event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        """Registrar evento de seguridad"""
        # En producción, enviar a sistema de logging/SIEM
        print(f"SECURITY_EVENT: {event_type} - User: {user_id} - Details: {details}")
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Enmascarar datos sensibles"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)


# Constantes del servicio
class Constants:
    """Constantes del servicio AuthProfiles"""
    
    # Límites
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_MINUTES = 30
    PASSWORD_HISTORY_COUNT = 5
    
    # Configuración de tokens
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Headers de seguridad
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }


# Funciones independientes para compatibilidad con auth_router_adapted
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashear contraseña usando bcrypt"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user():
    """Factory function que retorna una dependencia para obtener el usuario actual"""
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    
    security = HTTPBearer()
    
    async def _get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Función interna que obtiene el usuario del token JWT"""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se pudo validar las credenciales"
                )
            return payload
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales"
            )
    
    return _get_current_user