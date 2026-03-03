import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings


def create_access_token(user_id: int, role: str, permissions: list) -> str:
    """创建访问 Token"""
    now = datetime.utcnow()
    expire = now + timedelta(hours=settings.jwt_expire_hours)
    
    payload = {
        "user_id": user_id,
        "role": role,
        "permissions": permissions,
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> Optional[Dict]:
    """解码 Token"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except Exception as e:
        return None
