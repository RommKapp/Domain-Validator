import pytest
import asyncio
from unittest.mock import patch, MagicMock
import dns.resolver
import dns.exception
from app.services.dns_checker import DNSChecker

class TestDNSChecker:
    
    @pytest.fixture
    def dns_checker(self):
        return DNSChecker()

    @pytest.mark.asyncio
    async def test_check_mx_records_success(self, dns_checker):
        mock_records = [MagicMock()]
        mock_records[0].exchange = "mail.example.com"
        
        with patch('dns.resolver.resolve', return_value=mock_records):
            has_mx, mx_servers = await dns_checker.check_mx_records('example.com')
            
            assert has_mx == True
            assert mx_servers == ['mail.example.com']

    @pytest.mark.asyncio
    async def test_check_mx_records_no_records(self, dns_checker):
        with patch('dns.resolver.resolve', side_effect=dns.exception.DNSException()):
            has_mx, mx_servers = await dns_checker.check_mx_records('norecords.com')
            
            assert has_mx == False
            assert mx_servers == []

    @pytest.mark.asyncio
    async def test_check_a_records_success(self, dns_checker):
        mock_records = [MagicMock()]
        mock_records[0].__str__ = lambda x: "192.168.1.1"
        
        with patch('dns.resolver.resolve', return_value=mock_records):
            has_a = await dns_checker.check_a_records('example.com')
            
            assert has_a == True

    @pytest.mark.asyncio
    async def test_check_a_records_no_records(self, dns_checker):
        with patch('dns.resolver.resolve', side_effect=dns.exception.DNSException()):
            has_a = await dns_checker.check_a_records('norecords.com')
            
            assert has_a == False

    @pytest.mark.asyncio
    async def test_check_domain_exists_with_mx(self, dns_checker):
        with patch.object(dns_checker, 'check_mx_records', return_value=(True, ['mail.example.com'])), \
             patch.object(dns_checker, 'check_a_records', return_value=False):
            
            exists = await dns_checker.check_domain_exists('example.com')
            assert exists == True

    @pytest.mark.asyncio
    async def test_check_domain_exists_with_a_record(self, dns_checker):
        with patch.object(dns_checker, 'check_mx_records', return_value=(False, [])), \
             patch.object(dns_checker, 'check_a_records', return_value=True):
            
            exists = await dns_checker.check_domain_exists('example.com')
            assert exists == True

    @pytest.mark.asyncio
    async def test_check_domain_not_exists(self, dns_checker):
        with patch.object(dns_checker, 'check_mx_records', return_value=(False, [])), \
             patch.object(dns_checker, 'check_a_records', return_value=False):
            
            exists = await dns_checker.check_domain_exists('nonexistent.com')
            assert exists == False