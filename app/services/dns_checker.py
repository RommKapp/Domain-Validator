import socket
import dns.resolver
import dns.exception
from typing import List, Optional
import asyncio
import aiohttp

class DNSChecker:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        
    async def check_mx_records(self, domain: str) -> tuple[bool, List[str]]:
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._get_mx_records, domain)
            return True, result
        except Exception:
            return False, []
    
    def _get_mx_records(self, domain: str) -> List[str]:
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [str(record.exchange) for record in mx_records]
        except dns.exception.DNSException:
            return []
    
    async def check_a_records(self, domain: str) -> bool:
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._get_a_records, domain)
            return len(result) > 0
        except Exception:
            return False
    
    def _get_a_records(self, domain: str) -> List[str]:
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            return [str(record) for record in a_records]
        except dns.exception.DNSException:
            return []
    
    async def check_domain_exists(self, domain: str) -> bool:
        has_mx, _ = await self.check_mx_records(domain)
        has_a = await self.check_a_records(domain)
        return has_mx or has_a