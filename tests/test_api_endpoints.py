import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.schemas import DomainValidationResponse, DomainType, ValidationStatus, Recommendation, DomainMetadata
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_validation_response():
    return DomainValidationResponse(
        domain="example.com",
        domain_type=DomainType.CORPORATE,
        validation_status=ValidationStatus.VALID,
        quality_score=8.5,
        recommendation=Recommendation.ACCEPT,
        metadata=DomainMetadata(
            has_mx_record=True,
            has_a_record=True,
            mx_servers=["mail.example.com"],
            website_accessible=True,
            has_ssl_certificate=True
        ),
        checked_at=datetime.utcnow()
    )

class TestDomainEndpoints:
    
    @patch('app.api.endpoints.domain.get_validator')
    def test_validate_single_domain_success(self, mock_get_validator, mock_validation_response):
        mock_validator = AsyncMock()
        mock_validator.validate_domain.return_value = mock_validation_response
        mock_get_validator.return_value = mock_validator
        
        response = client.post("/api/v1/domain/validate", json={"domain": "example.com"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "example.com"
        assert data["domain_type"] == "corporate"
        assert data["validation_status"] == "valid"
        assert data["recommendation"] == "accept"

    @patch('app.api.endpoints.domain.get_validator')
    def test_validate_single_domain_with_email(self, mock_get_validator, mock_validation_response):
        mock_validator = AsyncMock()
        mock_validator.validate_domain.return_value = mock_validation_response
        mock_get_validator.return_value = mock_validator
        
        response = client.post("/api/v1/domain/validate", json={"domain": "user@example.com"})
        
        assert response.status_code == 200
        # Should extract domain from email
        mock_validator.validate_domain.assert_called_with("example.com")

    @patch('app.api.endpoints.domain.get_validator')
    def test_validate_batch_domains(self, mock_get_validator, mock_validation_response):
        mock_validator = AsyncMock()
        mock_validator.validate_domain.return_value = mock_validation_response
        mock_get_validator.return_value = mock_validator
        
        domains = ["example.com", "test.com"]
        response = client.post("/api/v1/domain/validate-batch", json={"domains": domains})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 2
        assert len(data["results"]) == 2
        assert "processing_time_seconds" in data

    @patch('app.api.endpoints.domain.get_validator')
    def test_validate_domain_error_handling(self, mock_get_validator):
        mock_validator = AsyncMock()
        mock_validator.validate_domain.side_effect = Exception("DNS lookup failed")
        mock_get_validator.return_value = mock_validator
        
        response = client.post("/api/v1/domain/validate", json={"domain": "invalid.domain"})
        
        assert response.status_code == 500
        assert "Validation failed" in response.json()["detail"]

    def test_health_check(self):
        response = client.get("/api/v1/domain/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "domain-validator"

    @patch('app.api.endpoints.domain.get_validator')
    def test_cache_stats(self, mock_get_validator):
        mock_validator = AsyncMock()
        mock_validator.cache_service.get_cache_stats.return_value = {
            "status": "connected",
            "used_memory": "1MB",
            "connected_clients": 1
        }
        mock_get_validator.return_value = mock_validator
        
        response = client.get("/api/v1/domain/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"

    @patch('app.api.endpoints.domain.get_validator')
    def test_invalidate_cache(self, mock_get_validator):
        mock_validator = AsyncMock()
        mock_validator.cache_service.invalidate_domain_cache.return_value = None
        mock_get_validator.return_value = mock_validator
        
        response = client.delete("/api/v1/domain/cache/example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert "Cache invalidated" in data["message"]

class TestWebEndpoints:
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_admin_endpoint(self):
        response = client.get("/admin")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestAppHealth:
    
    def test_app_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"