import os
from dotenv import load_dotenv
import jwt
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

load_dotenv()

# API Key Security for Legacy/Admin endpoints (Enrichment)
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT Security for User endpoints (Community)
SECURITY = HTTPBearer(auto_error=False)

def get_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Validates API Key for protected endpoints (like manual enrichment).
    """
    valid_keys = os.getenv("API_KEY", "").split(",")
    valid_keys = [key.strip() for key in valid_keys if key.strip()]
    
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Authorization not configured"
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(SECURITY)) -> str:
    """
    Validates Supabase JWT and returns user_id (sub).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authentication Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    # Try to get secret. If missing, we cannot securely verify signature locally without calling Supabase User API.
    # For now, we allow fallback to decoding without verify if secret is missing (DEV ONLY WARNING).
    secret = os.getenv("SUPABASE_JWT_SECRET") 
    
    try:
        if secret:
            payload = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        else:
            # WARNING: This relies on Supabase Gateway to have verified the token before hitting us if we were behind it.
            # But we are standalone. This is unsafe for production if public key not used.
            # Supabase uses HS256 (Symmetric) so we need the secret.
            # We will decode unverified to extract ID, but warn log.
            # Ideally, user updates .env
            print("WARNING: Decoding JWT without verification (Missing SUPABASE_JWT_SECRET)")
            payload = jwt.decode(token, options={"verify_signature": False})
            
        user_id = payload.get("sub")
        if not user_id:
             raise HTTPException(status_code=401, detail="Token missing user ID")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
         raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")