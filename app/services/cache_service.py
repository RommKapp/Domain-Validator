import redis.asyncio as aioredis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.schemas import DomainValidationResponse

class CacheService:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.ttl = settings.cache_ttl
        
    async def connect(self):
        try:
            self.redis_client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, domain: str) -> str:
        return f"domain_validation:{domain.lower()}"
    
    async def get_cached_validation(self, domain: str) -> Optional[DomainValidationResponse]:
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key(domain)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                # Convert back to Pydantic model
                return DomainValidationResponse(**data)
                
        except Exception as e:
            print(f"Cache get error: {e}")
            
        return None
    
    async def cache_validation_result(self, domain: str, result: DomainValidationResponse):
        if not self.redis_client:
            return
            
        try:
            cache_key = self._generate_cache_key(domain)
            # Convert Pydantic model to dict for JSON serialization
            data = result.model_dump(mode='json')
            
            await self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(data, default=str)
            )
            
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def invalidate_domain_cache(self, domain: str):
        if not self.redis_client:
            return
            
        try:
            cache_key = self._generate_cache_key(domain)
            await self.redis_client.delete(cache_key)
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        if not self.redis_client:
            return {"status": "disconnected"}
            
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}