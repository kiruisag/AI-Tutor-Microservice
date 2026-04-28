# app/core/security.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import jwt
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")