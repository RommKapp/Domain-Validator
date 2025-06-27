from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DomainType(str, Enum):
    CORPORATE = "corporate"
    PUBLIC_PROVIDER = "public_provider"
    DISPOSABLE = "disposable"
    EDUCATIONAL = "educational"
    GOVERNMENT = "government"
    UNREACHABLE = "unreachable"
    SUSPICIOUS = "suspicious"

class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"

class Recommendation(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    MANUAL_REVIEW = "manual_review"

class DomainValidationRequest(BaseModel):
    domain: str
    
    @validator('domain')
    def validate_domain(cls, v):
        if '@' in v:
            # Extract domain from email
            v = v.split('@')[1]
        return v.lower().strip()

class DomainMetadata(BaseModel):
    has_mx_record: bool = False
    has_a_record: bool = False
    mx_servers: Optional[List[str]] = None
    website_accessible: bool = False
    has_ssl_certificate: bool = False
    whois_registrar: Optional[str] = None
    whois_creation_date: Optional[datetime] = None
    whois_country: Optional[str] = None

class DomainValidationResponse(BaseModel):
    domain: str
    domain_type: DomainType
    validation_status: ValidationStatus
    quality_score: float
    recommendation: Recommendation
    metadata: DomainMetadata
    checked_at: datetime
    
class BatchValidationRequest(BaseModel):
    domains: List[str]
    
class BatchValidationResponse(BaseModel):
    results: List[DomainValidationResponse]
    total_processed: int
    processing_time_seconds: float