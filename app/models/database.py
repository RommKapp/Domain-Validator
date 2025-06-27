from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DomainType(enum.Enum):
    CORPORATE = "corporate"
    PUBLIC_PROVIDER = "public_provider"
    DISPOSABLE = "disposable"
    EDUCATIONAL = "educational"
    GOVERNMENT = "government"
    UNREACHABLE = "unreachable"
    SUSPICIOUS = "suspicious"

class ValidationStatus(enum.Enum):
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String(255), unique=True, index=True, nullable=False)
    domain_type = Column(Enum(DomainType), nullable=False)
    validation_status = Column(Enum(ValidationStatus), nullable=False)
    quality_score = Column(Float, default=0.0)
    
    # DNS Information
    has_mx_record = Column(Boolean, default=False)
    has_a_record = Column(Boolean, default=False)
    mx_servers = Column(Text)
    
    # HTTP Information
    website_accessible = Column(Boolean, default=False)
    has_ssl_certificate = Column(Boolean, default=False)
    
    # Metadata
    whois_registrar = Column(String(255))
    whois_creation_date = Column(DateTime)
    whois_country = Column(String(10))
    
    # Classification metadata
    is_whitelisted = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)
    manual_classification = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked_at = Column(DateTime, default=datetime.utcnow)

class DisposableDomainList(Base):
    __tablename__ = "disposable_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String(255), unique=True, index=True, nullable=False)
    source_list = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PublicProviderDomainList(Base):
    __tablename__ = "public_provider_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String(255), unique=True, index=True, nullable=False)
    provider_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()