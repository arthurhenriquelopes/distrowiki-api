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
    secret = os.getenv("SUPABASE_JWT_SECRET")
    
    try:
        if secret:
            # Try with audience first
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
            except jwt.InvalidAudienceError:
                # Fallback: try without audience requirement (some Supabase configs may differ)
                print("WARNING: JWT audience mismatch, retrying without audience check")
                payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
        else:
            print("WARNING: Decoding JWT without verification (Missing SUPABASE_JWT_SECRET)")
            payload = jwt.decode(token, options={"verify_signature": False})
            
        user_id = payload.get("sub")
        if not user_id:
             raise HTTPException(status_code=401, detail="Token missing user ID")
        return user_id

    except jwt.ExpiredSignatureError:
        print("JWT Error: Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"JWT Error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")