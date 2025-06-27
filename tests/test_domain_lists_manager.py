import pytest
import asyncio
from unittest.mock import patch, AsyncMock, mock_open
import aiohttp
from app.services.domain_lists_manager import DomainListsManager

class TestDomainListsManager:
    
    @pytest.fixture
    def domain_lists_manager(self):
        return DomainListsManager()

    @pytest.mark.asyncio
    async def test_fetch_domain_list_success(self, domain_lists_manager):
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "example.com\ntest.com\n# Comment\ninvalid_line"
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await domain_lists_manager._fetch_domain_list(mock_session, "http://example.com/list.txt")
        
        assert result == ["example.com", "test.com"]

    @pytest.mark.asyncio
    async def test_fetch_domain_list_http_error(self, domain_lists_manager):
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await domain_lists_manager._fetch_domain_list(mock_session, "http://example.com/notfound.txt")
        
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_domain_list_exception(self, domain_lists_manager):
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Network error")
        
        result = await domain_lists_manager._fetch_domain_list(mock_session, "http://example.com/error.txt")
        
        assert result == []

    @pytest.mark.asyncio
    async def test_load_hubspot_list_success(self, domain_lists_manager):
        csv_content = "gmail.com\nyahoo.com\noutlook.com\n"
        
        with patch('builtins.open', mock_open(read_data=csv_content)):
            result = await domain_lists_manager._load_hubspot_list()
            
            assert result == ["gmail.com", "yahoo.com", "outlook.com"]

    @pytest.mark.asyncio
    async def test_load_hubspot_list_file_not_found(self, domain_lists_manager):
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = await domain_lists_manager._load_hubspot_list()
            
            assert result == []

    @pytest.mark.asyncio
    async def test_update_disposable_lists(self, domain_lists_manager):
        # Mock the fetch methods
        with patch.object(domain_lists_manager, '_fetch_domain_list', return_value=['temp.com', 'disposable.com']), \
             patch.object(domain_lists_manager, '_load_hubspot_list', return_value=['gmail.com', 'yahoo.com']):
            
            results = await domain_lists_manager.update_disposable_lists()
            
            # Check that disposable domains were added
            assert 'temp.com' in domain_lists_manager.disposable_domains
            assert 'disposable.com' in domain_lists_manager.disposable_domains
            
            # Check that HubSpot domains were added to public providers
            assert 'gmail.com' in domain_lists_manager.public_provider_domains
            assert 'yahoo.com' in domain_lists_manager.public_provider_domains
            
            # Check results structure
            assert len(results) > 0
            assert 'hubspot_list' in results

    def test_is_disposable_domain(self, domain_lists_manager):
        domain_lists_manager.disposable_domains.add('tempmail.com')
        
        assert domain_lists_manager.is_disposable_domain('tempmail.com') == True
        assert domain_lists_manager.is_disposable_domain('TEMPMAIL.COM') == True  # Case insensitive
        assert domain_lists_manager.is_disposable_domain('gmail.com') == False

    def test_is_public_provider(self, domain_lists_manager):
        assert domain_lists_manager.is_public_provider('gmail.com') == True
        assert domain_lists_manager.is_public_provider('GMAIL.COM') == True  # Case insensitive
        assert domain_lists_manager.is_public_provider('example.com') == False

    def test_get_domain_category(self, domain_lists_manager):
        domain_lists_manager.disposable_domains.add('tempmail.com')
        
        assert domain_lists_manager.get_domain_category('tempmail.com') == 'disposable'
        assert domain_lists_manager.get_domain_category('gmail.com') == 'public_provider'
        assert domain_lists_manager.get_domain_category('example.com') == 'unknown'

    @pytest.mark.asyncio
    async def test_initialize(self, domain_lists_manager):
        with patch.object(domain_lists_manager, 'update_disposable_lists', return_value={}):
            await domain_lists_manager.initialize()
            # Should complete without error