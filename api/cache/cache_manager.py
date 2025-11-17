"""
Gerenciador de cache para dados da API.

Implementa cache em JSON com TTL de 24 horas, com suporte opcional
para Redis/KV para deploy em produção.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import os

from ..models.distro import DistroMetadata

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerenciador de cache para distribuições Linux.
    
    Suporta dois backends:
    - JSON: cache local em arquivo (desenvolvimento)
    - Redis/KV: cache distribuído (produção - futuro)
    
    TTL padrão: 24 horas (conforme especificação do Módulo 1)
    """
    
    DEFAULT_TTL = 86400  # 24 horas em segundos
    CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
    DISTROS_CACHE_FILE = "distros_cache.json"
    
    def __init__(self, use_redis: bool = False):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            use_redis: Se deve usar Redis em vez de JSON (futuro).
        """
        self.use_redis = use_redis
        self.redis_client = None
        self._memory_cache = {}  # Sempre inicializar com cache em memória como fallback
        self._use_file_cache = True  # Flag para saber se pode usar arquivo
        
        # Tentar criar diretório de cache
        try:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory ready: {self.CACHE_DIR}")
        except Exception as e:
            logger.warning(f"Não é possível usar cache em arquivo ({e}). Usando apenas cache em memória.")
            self._use_file_cache = False
        
        if use_redis:
            self._init_redis()
    
    def _init_redis(self):
        """Inicializa cliente Redis (implementação futura)."""
        # TODO: Implementar quando necessário para produção
        logger.warning("Redis não implementado ainda, usando JSON como fallback")
        self.use_redis = False
    
    @property
    def cache_file_path(self) -> Path:
        """Caminho do arquivo de cache JSON."""
        return self.CACHE_DIR / self.DISTROS_CACHE_FILE
    
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """
        Verifica se o cache ainda é válido (não expirou).
        
        Args:
            cache_data: Dados do cache.
        
        Returns:
            True se o cache é válido, False caso contrário.
        """
        timestamp_str = cache_data.get("timestamp")
        if not timestamp_str:
            return False
        
        try:
            cache_time = datetime.fromisoformat(timestamp_str)
            expiry_time = cache_time + timedelta(seconds=self.DEFAULT_TTL)
            return datetime.utcnow() < expiry_time
        except Exception as e:
            logger.warning(f"Erro ao validar cache: {e}")
            return False
    
    def get_distros_cache(self) -> Optional[List[DistroMetadata]]:
        """
        Recupera lista de distribuições do cache.
        
        Returns:
            Lista de DistroMetadata ou None se cache inválido/inexistente.
        """
        try:
            # Sempre tentar cache em memória primeiro
            if "distros" in self._memory_cache:
                cache_data = self._memory_cache["distros"]
                if self._is_cache_valid(cache_data):
                    distros_data = cache_data.get("distros", [])
                    distros = [
                        DistroMetadata(**distro_dict) 
                        for distro_dict in distros_data
                    ]
                    logger.info(f"Cache em memória recuperado: {len(distros)} distribuições")
                    return distros
            
            # Se não há cache em memória, tentar arquivo
            if not self._use_file_cache:
                logger.info("Nenhum cache disponível")
                return None
            
            if not self.cache_file_path.exists():
                logger.info("Cache em arquivo não encontrado")
                return None
            
            with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar validade do cache
            if not self._is_cache_valid(cache_data):
                logger.info("Cache em arquivo expirado")
                return None
            
            # Converter dicionários para objetos DistroMetadata
            distros_data = cache_data.get("distros", [])
            distros = [
                DistroMetadata(**distro_dict) 
                for distro_dict in distros_data
            ]
            
            # Salvar em memória também
            self._memory_cache["distros"] = cache_data
            
            logger.info(f"Cache em arquivo recuperado: {len(distros)} distribuições")
            return distros
            
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None
    
    def set_distros_cache(self, distros: List[DistroMetadata]) -> bool:
        """
        Salva lista de distribuições no cache.
        
        Args:
            distros: Lista de distribuições para cachear.
        
        Returns:
            True se salvou com sucesso, False caso contrário.
        """
        try:
            cache_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "ttl_seconds": self.DEFAULT_TTL,
                "count": len(distros),
                "distros": [
                    distro.model_dump(mode='json') 
                    for distro in distros
                ]
            }
            
            # Sempre salvar em memória
            self._memory_cache["distros"] = cache_data
            logger.info(f"Cache em memória atualizado: {len(distros)} distribuições")
            
            # Tentar salvar em arquivo também
            if self._use_file_cache:
                try:
                    with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
                    logger.info(f"Cache em arquivo atualizado: {len(distros)} distribuições")
                except Exception as e:
                    logger.warning(f"Não foi possível salvar cache em arquivo: {e}. Cache em memória OK.")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre o cache atual.
        
        Returns:
            Dicionário com metadados do cache ou None.
        """
        try:
            if not self.cache_file_path.exists():
                return None
            
            with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp_str = cache_data.get("timestamp")
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
            
            is_valid = self._is_cache_valid(cache_data)
            
            expiry = None
            if timestamp:
                expiry = timestamp + timedelta(seconds=self.DEFAULT_TTL)
            
            return {
                "valid": is_valid,
                "timestamp": timestamp,
                "expiry": expiry,
                "count": cache_data.get("count", 0),
                "ttl_seconds": cache_data.get("ttl_seconds", self.DEFAULT_TTL)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter info do cache: {e}")
            return None
    
    def invalidate_cache(self) -> bool:
        """
        Invalida/remove o cache atual.
        
        Returns:
            True se invalidou com sucesso.
        """
        try:
            # Se usando cache em memória
            if self._memory_cache is not None:
                self._memory_cache.clear()
                logger.info("Cache em memória invalidado")
                return True
            
            if self.cache_file_path.exists():
                self.cache_file_path.unlink()
                logger.info("Cache invalidado")
            return True
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return False
    
    def get_or_fetch(
        self, 
        fetch_func: callable,
        force_refresh: bool = False
    ) -> List[DistroMetadata]:
        """
        Retorna dados do cache ou busca novos se necessário.
        
        Args:
            fetch_func: Função assíncrona para buscar dados novos.
            force_refresh: Se deve forçar atualização mesmo com cache válido.
        
        Returns:
            Lista de distribuições.
        """
        # Se forçar refresh, invalidar cache
        if force_refresh:
            self.invalidate_cache()
        
        # Tentar recuperar do cache
        cached_distros = self.get_distros_cache()
        
        if cached_distros is not None:
            return cached_distros
        
        # Cache inválido/inexistente, buscar novos dados
        logger.info("Buscando novos dados...")
        # Nota: fetch_func deve ser chamada com await no contexto async
        # Esta função será usada de forma síncrona, então retornamos None
        # para indicar que precisa buscar
        return None


# Singleton do gerenciador de cache
_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Retorna instância singleton do gerenciador de cache.
    
    Returns:
        Instância do CacheManager.
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        # Verificar se deve usar Redis via variável de ambiente
        use_redis = os.getenv("USE_REDIS_CACHE", "false").lower() == "true"
        _cache_manager_instance = CacheManager(use_redis=use_redis)
    
    return _cache_manager_instance
