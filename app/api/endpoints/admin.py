from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.models.database import get_db, Domain, DomainType, ValidationStatus
from app.services.domain_validator import DomainValidator

router = APIRouter(prefix="/admin", tags=["admin"])

class WhitelistRequest(BaseModel):
    domain: str
    notes: str = ""

class BlacklistRequest(BaseModel):
    domain: str
    notes: str = ""

class DomainOverrideRequest(BaseModel):
    domain: str
    domain_type: DomainType
    notes: str = ""

async def get_validator() -> DomainValidator:
    validator = DomainValidator()
    await validator.cache_service.connect()
    await validator.domain_lists.initialize()
    return validator

@router.post("/whitelist")
async def add_to_whitelist(
    request: WhitelistRequest, 
    db: Session = Depends(get_db),
    validator: DomainValidator = Depends(get_validator)
):
    try:
        # Check if domain already exists
        existing_domain = db.query(Domain).filter(Domain.domain_name == request.domain).first()
        
        if existing_domain:
            # Update existing domain
            existing_domain.is_whitelisted = True
            existing_domain.is_blacklisted = False
            existing_domain.manual_classification = True
            existing_domain.notes = request.notes
        else:
            # Create new domain record
            new_domain = Domain(
                domain_name=request.domain,
                domain_type=DomainType.CORPORATE,
                validation_status=ValidationStatus.VALID,
                quality_score=10.0,
                is_whitelisted=True,
                is_blacklisted=False,
                manual_classification=True,
                notes=request.notes
            )
            db.add(new_domain)
        
        db.commit()
        
        # Invalidate cache
        await validator.cache_service.invalidate_domain_cache(request.domain)
        
        return {"message": f"Domain {request.domain} added to whitelist"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blacklist")
async def add_to_blacklist(
    request: BlacklistRequest, 
    db: Session = Depends(get_db),
    validator: DomainValidator = Depends(get_validator)
):
    try:
        # Check if domain already exists
        existing_domain = db.query(Domain).filter(Domain.domain_name == request.domain).first()
        
        if existing_domain:
            # Update existing domain
            existing_domain.is_blacklisted = True
            existing_domain.is_whitelisted = False
            existing_domain.manual_classification = True
            existing_domain.domain_type = DomainType.SUSPICIOUS
            existing_domain.validation_status = ValidationStatus.SUSPICIOUS
            existing_domain.quality_score = 0.0
            existing_domain.notes = request.notes
        else:
            # Create new domain record
            new_domain = Domain(
                domain_name=request.domain,
                domain_type=DomainType.SUSPICIOUS,
                validation_status=ValidationStatus.SUSPICIOUS,
                quality_score=0.0,
                is_whitelisted=False,
                is_blacklisted=True,
                manual_classification=True,
                notes=request.notes
            )
            db.add(new_domain)
        
        db.commit()
        
        # Invalidate cache
        await validator.cache_service.invalidate_domain_cache(request.domain)
        
        return {"message": f"Domain {request.domain} added to blacklist"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/whitelist/{domain}")
async def remove_from_whitelist(
    domain: str, 
    db: Session = Depends(get_db),
    validator: DomainValidator = Depends(get_validator)
):
    try:
        existing_domain = db.query(Domain).filter(Domain.domain_name == domain).first()
        
        if not existing_domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        existing_domain.is_whitelisted = False
        existing_domain.manual_classification = False
        db.commit()
        
        # Invalidate cache
        await validator.cache_service.invalidate_domain_cache(domain)
        
        return {"message": f"Domain {domain} removed from whitelist"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/blacklist/{domain}")
async def remove_from_blacklist(
    domain: str, 
    db: Session = Depends(get_db),
    validator: DomainValidator = Depends(get_validator)
):
    try:
        existing_domain = db.query(Domain).filter(Domain.domain_name == domain).first()
        
        if not existing_domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        existing_domain.is_blacklisted = False
        existing_domain.manual_classification = False
        db.commit()
        
        # Invalidate cache
        await validator.cache_service.invalidate_domain_cache(domain)
        
        return {"message": f"Domain {domain} removed from blacklist"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whitelist")
async def get_whitelisted_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).filter(Domain.is_whitelisted == True).all()
    return [{"domain": d.domain_name, "notes": d.notes, "added_at": d.created_at} for d in domains]

@router.get("/blacklist")
async def get_blacklisted_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).filter(Domain.is_blacklisted == True).all()
    return [{"domain": d.domain_name, "notes": d.notes, "added_at": d.created_at} for d in domains]

@router.post("/override")
async def override_domain_classification(
    request: DomainOverrideRequest,
    db: Session = Depends(get_db),
    validator: DomainValidator = Depends(get_validator)
):
    try:
        existing_domain = db.query(Domain).filter(Domain.domain_name == request.domain).first()
        
        if existing_domain:
            existing_domain.domain_type = request.domain_type
            existing_domain.manual_classification = True
            existing_domain.notes = request.notes
        else:
            # Create new domain record
            new_domain = Domain(
                domain_name=request.domain,
                domain_type=request.domain_type,
                validation_status=ValidationStatus.VALID,
                quality_score=5.0,
                manual_classification=True,
                notes=request.notes
            )
            db.add(new_domain)
        
        db.commit()
        
        # Invalidate cache
        await validator.cache_service.invalidate_domain_cache(request.domain)
        
        return {"message": f"Domain {request.domain} classification overridden to {request.domain_type}"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    total_domains = db.query(Domain).count()
    whitelisted = db.query(Domain).filter(Domain.is_whitelisted == True).count()
    blacklisted = db.query(Domain).filter(Domain.is_blacklisted == True).count()
    manual_overrides = db.query(Domain).filter(Domain.manual_classification == True).count()
    
    return {
        "total_domains": total_domains,
        "whitelisted": whitelisted,
        "blacklisted": blacklisted,
        "manual_overrides": manual_overrides
    }