"""
Módulo de segurança e autenticação da API.
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader


# Header onde a API Key deve vir
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Valida API Key para endpoints protegidos.
    
    Args:
        api_key: API Key do header X-API-Key
    
    Returns:
        API Key válida
    
    Raises:
        HTTPException: Se API Key inválida ou ausente
    """
    # Buscar API Keys válidas do ambiente
    valid_keys = os.getenv("API_KEYS", "").split(",")
    valid_keys = [key.strip() for key in valid_keys if key.strip()]
    
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API Keys não configuradas no servidor"
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key não fornecida. Use o header X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida"
        )
    
    return api_key