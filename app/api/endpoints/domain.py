from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import time
from app.services.domain_validator import DomainValidator
from app.models.schemas import (
    DomainValidationRequest, DomainValidationResponse, 
    BatchValidationRequest, BatchValidationResponse
)

router = APIRouter(prefix="/domain", tags=["domain"])

# Dependency to get validator instance
async def get_validator() -> DomainValidator:
    validator = DomainValidator()
    await validator.cache_service.connect()
    await validator.domain_lists.initialize()
    return validator

@router.post("/validate", response_model=DomainValidationResponse)
async def validate_domain(
    request: DomainValidationRequest,
    validator: DomainValidator = Depends(get_validator)
):
    try:
        result = await validator.validate_domain(request.domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/validate-batch", response_model=BatchValidationResponse)
async def validate_domains_batch(
    request: BatchValidationRequest,
    validator: DomainValidator = Depends(get_validator)
):
    try:
        start_time = time.time()
        results = []
        
        for domain in request.domains:
            try:
                result = await validator.validate_domain(domain)
                results.append(result)
            except Exception as domain_error:
                # Continue processing other domains even if one fails
                continue
        
        processing_time = time.time() - start_time
        
        return BatchValidationResponse(
            results=results,
            total_processed=len(results),
            processing_time_seconds=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch validation failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "domain-validator"}

@router.get("/cache/stats")
async def get_cache_stats(validator: DomainValidator = Depends(get_validator)):
    try:
        stats = await validator.cache_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats error: {str(e)}")

@router.delete("/cache/{domain}")
async def invalidate_domain_cache(
    domain: str,
    validator: DomainValidator = Depends(get_validator)
):
    try:
        await validator.cache_service.invalidate_domain_cache(domain)
        return {"message": f"Cache invalidated for domain: {domain}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")