import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.domain_validator import DomainValidator
from app.services.dns_checker import DNSChecker
from app.services.http_checker import HTTPChecker
from app.models.schemas import DomainType, ValidationStatus, Recommendation

@pytest.fixture
def domain_validator():
    validator = DomainValidator()
    return validator

@pytest.fixture
def mock_dns_results():
    return {
        'has_mx': True,
        'has_a': True,
        'mx_servers': ['mail.example.com'],
        'domain_exists': True
    }

@pytest.fixture
def mock_http_results():
    return {
        'accessible': True,
        'has_ssl': True,
        'status_code': 200,
        'ssl_valid': True
    }

class TestDomainValidator:
    
    @pytest.mark.asyncio
    async def test_validate_corporate_domain(self, domain_validator, mock_dns_results, mock_http_results):
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns_results), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http_results), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('example.com')
            
            assert result.domain == 'example.com'
            assert result.domain_type == DomainType.CORPORATE
            assert result.validation_status == ValidationStatus.VALID
            assert result.quality_score >= 7.0
            assert result.recommendation == Recommendation.ACCEPT

    @pytest.mark.asyncio
    async def test_validate_disposable_domain(self, domain_validator):
        # Mock disposable domain
        domain_validator.domain_lists.disposable_domains.add('tempmail.com')
        
        mock_dns = {'has_mx': True, 'has_a': True, 'mx_servers': ['mx.tempmail.com'], 'domain_exists': True}
        mock_http = {'accessible': True, 'has_ssl': False, 'status_code': 200, 'ssl_valid': False}
        
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('tempmail.com')
            
            assert result.domain == 'tempmail.com'
            assert result.domain_type == DomainType.DISPOSABLE
            assert result.recommendation == Recommendation.REJECT

    @pytest.mark.asyncio
    async def test_validate_unreachable_domain(self, domain_validator):
        mock_dns = {'has_mx': False, 'has_a': False, 'mx_servers': [], 'domain_exists': False}
        mock_http = {'accessible': False, 'has_ssl': False, 'status_code': None, 'ssl_valid': False}
        
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('nonexistent.domain')
            
            assert result.domain == 'nonexistent.domain'
            assert result.domain_type == DomainType.UNREACHABLE
            assert result.validation_status == ValidationStatus.INVALID
            assert result.quality_score == 0.0
            assert result.recommendation == Recommendation.REJECT

    @pytest.mark.asyncio
    async def test_validate_educational_domain(self, domain_validator, mock_dns_results, mock_http_results):
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns_results), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http_results), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('harvard.edu')
            
            assert result.domain == 'harvard.edu'
            assert result.domain_type == DomainType.EDUCATIONAL
            assert result.recommendation == Recommendation.ACCEPT

    @pytest.mark.asyncio
    async def test_validate_government_domain(self, domain_validator, mock_dns_results, mock_http_results):
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns_results), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http_results), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('whitehouse.gov')
            
            assert result.domain == 'whitehouse.gov'
            assert result.domain_type == DomainType.GOVERNMENT
            assert result.recommendation == Recommendation.ACCEPT

    @pytest.mark.asyncio
    async def test_validate_public_provider(self, domain_validator, mock_dns_results, mock_http_results):
        # Mock public provider
        domain_validator.domain_lists.public_provider_domains.add('gmail.com')
        
        with patch.object(domain_validator, '_perform_dns_checks', return_value=mock_dns_results), \
             patch.object(domain_validator, '_perform_http_checks', return_value=mock_http_results), \
             patch.object(domain_validator.cache_service, 'get_cached_validation', return_value=None), \
             patch.object(domain_validator.cache_service, 'cache_validation_result'):
            
            result = await domain_validator.validate_domain('gmail.com')
            
            assert result.domain == 'gmail.com'
            assert result.domain_type == DomainType.PUBLIC_PROVIDER
            assert result.recommendation == Recommendation.MANUAL_REVIEW

    def test_is_educational_domain(self, domain_validator):
        assert domain_validator._is_educational_domain('harvard.edu') == True
        assert domain_validator._is_educational_domain('oxford.ac.uk') == True
        assert domain_validator._is_educational_domain('google.com') == False

    def test_is_government_domain(self, domain_validator):
        assert domain_validator._is_government_domain('whitehouse.gov') == True
        assert domain_validator._is_government_domain('parliament.gov.uk') == True
        assert domain_validator._is_government_domain('google.com') == False

    def test_is_suspicious_domain(self, domain_validator):
        mock_dns = {'has_mx': False, 'has_a': True, 'mx_servers': [], 'domain_exists': True}
        mock_http = {'accessible': False, 'has_ssl': False, 'status_code': None, 'ssl_valid': False}
        
        # Test suspicious patterns
        assert domain_validator._is_suspicious_domain('fake-bank.com', mock_dns, mock_http) == True
        assert domain_validator._is_suspicious_domain('test-spam.tk', mock_dns, mock_http) == True
        assert domain_validator._is_suspicious_domain('mailtest.ml', mock_dns, mock_http) == True
        
        # Test normal domain
        mock_dns_good = {'has_mx': True, 'has_a': True, 'mx_servers': ['mx.example.com'], 'domain_exists': True}
        assert domain_validator._is_suspicious_domain('example.com', mock_dns_good, mock_http) == False

    def test_calculate_quality_score(self, domain_validator):
        mock_dns = {'has_mx': True, 'has_a': True, 'mx_servers': ['mx.example.com'], 'domain_exists': True}
        mock_http = {'accessible': True, 'has_ssl': True, 'status_code': 200, 'ssl_valid': True}
        
        # Corporate domain with all good indicators
        score = domain_validator._calculate_quality_score(DomainType.CORPORATE, mock_dns, mock_http)
        assert score >= 8.0
        
        # Disposable domain
        score = domain_validator._calculate_quality_score(DomainType.DISPOSABLE, mock_dns, mock_http)
        assert score <= 3.0
        
        # Unreachable domain
        mock_dns_bad = {'has_mx': False, 'has_a': False, 'mx_servers': [], 'domain_exists': False}
        mock_http_bad = {'accessible': False, 'has_ssl': False, 'status_code': None, 'ssl_valid': False}
        score = domain_validator._calculate_quality_score(DomainType.UNREACHABLE, mock_dns_bad, mock_http_bad)
        assert score == 0.0

    def test_generate_recommendation(self, domain_validator):
        # High quality corporate domain
        rec = domain_validator._generate_recommendation(DomainType.CORPORATE, 9.0)
        assert rec == Recommendation.ACCEPT
        
        # Disposable domain
        rec = domain_validator._generate_recommendation(DomainType.DISPOSABLE, 2.0)
        assert rec == Recommendation.REJECT
        
        # Low quality domain
        rec = domain_validator._generate_recommendation(DomainType.SUSPICIOUS, 2.5)
        assert rec == Recommendation.REJECT
        
        # Medium quality domain
        rec = domain_validator._generate_recommendation(DomainType.CORPORATE, 5.0)
        assert rec == Recommendation.MANUAL_REVIEW