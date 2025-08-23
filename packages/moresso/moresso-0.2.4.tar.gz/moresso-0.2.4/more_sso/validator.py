
import json
import jwt
from more_sso.cache import Cache
from more_sso.config import get_sso_config,get_pem
from more_sso.exceptions import JWTValidationError

_public_key_cache = Cache(ttl_seconds=60*60)

def get_public_key() -> str:
    cached_key = _public_key_cache.get('PUBLIC_KEY')
    if cached_key:
        return cached_key

    cfg = get_sso_config()
    public_key = get_pem(cfg['public_key_uri'])

    _public_key_cache.set('PUBLIC_KEY', public_key)
    return public_key
 

def validate_jwt(token: str) -> dict:
    public_key = get_public_key()
    try:
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1].strip()
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"]
        )
        return payload
    except Exception as e:
        _public_key_cache.clear()
        raise JWTValidationError(f"JWT validation failed: {str(e)}")

def validate_token(token) -> dict:
    cfg = get_sso_config()
    user = validate_jwt(token)
    return user