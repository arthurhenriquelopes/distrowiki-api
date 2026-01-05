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
    Supports both HS256 (legacy) and ES256 (new Supabase default) algorithms.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authentication Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    
    try:
        # First, decode header to check algorithm
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "HS256")
        
        if algorithm == "ES256":
            # ES256 uses asymmetric keys - need to fetch from JWKS
            # Get Supabase URL from environment
            supabase_url = os.getenv("SUPABASE_URL", "")
            if not supabase_url:
                print("ERROR: SUPABASE_URL not set, cannot validate ES256 token")
                raise HTTPException(status_code=401, detail="Server configuration error")
            
            # Fetch JWKS from Supabase
            import urllib.request
            import json
            jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
            
            try:
                with urllib.request.urlopen(jwks_url, timeout=5) as response:
                    jwks = json.loads(response.read().decode())
            except Exception as e:
                print(f"ERROR: Failed to fetch JWKS: {e}")
                raise HTTPException(status_code=401, detail="Failed to validate token")
            
            # Find the correct key by kid
            kid = unverified_header.get("kid")
            public_key = None
            
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    # Convert JWK to PEM format
                    from jwt.algorithms import ECAlgorithm
                    public_key = ECAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                print(f"ERROR: Key {kid} not found in JWKS")
                raise HTTPException(status_code=401, detail="Token key not found")
            
            payload = jwt.decode(
                token, 
                public_key, 
                algorithms=["ES256"], 
                audience="authenticated"
            )
        else:
            # HS256 uses symmetric secret
            secret = os.getenv("SUPABASE_JWT_SECRET")
            if not secret:
                print("WARNING: Decoding JWT without verification (Missing SUPABASE_JWT_SECRET)")
                payload = jwt.decode(token, options={"verify_signature": False})
            else:
                try:
                    payload = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
                except jwt.InvalidAudienceError:
                    print("WARNING: JWT audience mismatch, retrying without audience check")
                    payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
            
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