import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from app.services.dns_checker import DNSChecker
from app.services.http_checker import HTTPChecker
from app.services.domain_lists_manager import DomainListsManager
from app.services.cache_service import CacheService
from app.models.schemas import (
    DomainValidationResponse, DomainType, ValidationStatus, 
    Recommendation, DomainMetadata
)

class DomainValidator:
    def __init__(self):
        self.dns_checker = DNSChecker()
        self.http_checker = HTTPChecker()
        self.domain_lists = DomainListsManager()
        self.cache_service = CacheService()
        
    async def validate_domain(self, domain: str) -> DomainValidationResponse:
        domain = domain.lower().strip()
        
        # Check cache first
        cached_result = await self.cache_service.get_cached_validation(domain)
        if cached_result:
            return cached_result
        
        # Parallel execution of checks
        dns_task = self._perform_dns_checks(domain)
        http_task = self._perform_http_checks(domain)
        
        dns_results, http_results = await asyncio.gather(dns_task, http_task)
        
        # Combine results
        metadata = DomainMetadata(
            has_mx_record=dns_results['has_mx'],
            has_a_record=dns_results['has_a'],
            mx_servers=dns_results['mx_servers'],
            website_accessible=http_results['accessible'],
            has_ssl_certificate=http_results['has_ssl']
        )
        
        # Classify domain
        domain_type = await self._classify_domain(domain, dns_results, http_results)
        validation_status = self._determine_validation_status(dns_results, http_results)
        quality_score = self._calculate_quality_score(domain_type, dns_results, http_results)
        recommendation = self._generate_recommendation(domain_type, quality_score)
        
        result = DomainValidationResponse(
            domain=domain,
            domain_type=domain_type,
            validation_status=validation_status,
            quality_score=quality_score,
            recommendation=recommendation,
            metadata=metadata,
            checked_at=datetime.utcnow()
        )
        
        # Cache the result
        await self.cache_service.cache_validation_result(domain, result)
        
        return result
    
    async def _perform_dns_checks(self, domain: str) -> Dict[str, Any]:
        has_mx, mx_servers = await self.dns_checker.check_mx_records(domain)
        has_a = await self.dns_checker.check_a_records(domain)
        
        return {
            'has_mx': has_mx,
            'has_a': has_a,
            'mx_servers': mx_servers,
            'domain_exists': has_mx or has_a
        }
    
    async def _perform_http_checks(self, domain: str) -> Dict[str, Any]:
        website_check = await self.http_checker.check_website_accessibility(domain)
        ssl_check = await self.http_checker.check_ssl_certificate(domain)
        
        return {
            'accessible': website_check['accessible'],
            'has_ssl': ssl_check['has_ssl'] or website_check['has_ssl'],
            'status_code': website_check['status_code'],
            'ssl_valid': ssl_check['valid_ssl']
        }
    
    async def _classify_domain(self, domain: str, dns_results: Dict, http_results: Dict) -> DomainType:
        if not dns_results['domain_exists']:
            return DomainType.UNREACHABLE
            
        # Check disposable domains first
        if self.domain_lists.is_disposable_domain(domain):
            return DomainType.DISPOSABLE
            
        # Check public providers
        if self.domain_lists.is_public_provider(domain):
            return DomainType.PUBLIC_PROVIDER
            
        # Check for educational domains
        if self._is_educational_domain(domain):
            return DomainType.EDUCATIONAL
            
        # Check for government domains
        if self._is_government_domain(domain):
            return DomainType.GOVERNMENT
            
        # Check for suspicious indicators
        if self._is_suspicious_domain(domain, dns_results, http_results):
            return DomainType.SUSPICIOUS
            
        # Default to corporate if has proper infrastructure
        if dns_results['has_mx'] and http_results['accessible']:
            return DomainType.CORPORATE
            
        return DomainType.SUSPICIOUS
    
    def _is_educational_domain(self, domain: str) -> bool:
        edu_tlds = ['.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.za', '.edu.sg']
        return any(domain.endswith(tld) for tld in edu_tlds)
    
    def _is_government_domain(self, domain: str) -> bool:
        gov_tlds = ['.gov', '.gov.uk', '.gov.au', '.gov.ca', '.gouv.fr', '.gob.es']
        return any(domain.endswith(tld) for tld in gov_tlds)
    
    def _is_suspicious_domain(self, domain: str, dns_results: Dict, http_results: Dict) -> bool:
        # Check for suspicious patterns
        suspicious_patterns = [
            'temp', 'fake', 'test', 'spam', 'trash', 'disposable',
            'guerrilla', 'mailinator', 'throwaway', 'burner'
        ]
        
        domain_lower = domain.lower()
        for pattern in suspicious_patterns:
            if pattern in domain_lower:
                return True
        
        # Check for very new domains or unusual TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.top', '.click', '.download']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            return True
            
        # No MX records but trying to be an email service
        if not dns_results['has_mx'] and 'mail' in domain_lower:
            return True
            
        return False
    
    def _determine_validation_status(self, dns_results: Dict, http_results: Dict) -> ValidationStatus:
        if not dns_results['domain_exists']:
            return ValidationStatus.INVALID
            
        if dns_results['has_mx'] and dns_results['has_a']:
            return ValidationStatus.VALID
            
        if dns_results['has_mx'] or dns_results['has_a']:
            return ValidationStatus.SUSPICIOUS
            
        return ValidationStatus.UNKNOWN
    
    def _calculate_quality_score(self, domain_type: DomainType, dns_results: Dict, http_results: Dict) -> float:
        score = 0.0
        
        # Base score by type
        type_scores = {
            DomainType.CORPORATE: 8.0,
            DomainType.EDUCATIONAL: 7.0,
            DomainType.GOVERNMENT: 9.0,
            DomainType.PUBLIC_PROVIDER: 5.0,
            DomainType.DISPOSABLE: 1.0,
            DomainType.SUSPICIOUS: 2.0,
            DomainType.UNREACHABLE: 0.0
        }
        
        score = type_scores.get(domain_type, 3.0)
        
        # Adjust for technical factors
        if dns_results['has_mx']:
            score += 0.5
        if dns_results['has_a']:
            score += 0.3
        if http_results['accessible']:
            score += 0.5
        if http_results['has_ssl']:
            score += 0.7
            
        return min(10.0, max(0.0, score))
    
    def _generate_recommendation(self, domain_type: DomainType, quality_score: float) -> Recommendation:
        if domain_type == DomainType.DISPOSABLE or quality_score < 3.0:
            return Recommendation.REJECT
            
        if domain_type == DomainType.CORPORATE and quality_score >= 7.0:
            return Recommendation.ACCEPT
            
        if domain_type == DomainType.EDUCATIONAL or domain_type == DomainType.GOVERNMENT:
            return Recommendation.ACCEPT
            
        return Recommendation.MANUAL_REVIEW