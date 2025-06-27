import aiohttp
import ssl
import socket
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class HTTPChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
    async def check_website_accessibility(self, domain: str) -> Dict[str, Any]:
        results = {
            'accessible': False,
            'has_ssl': False,
            'status_code': None,
            'redirects': 0,
            'final_url': None
        }
        
        urls_to_try = [f"https://{domain}", f"http://{domain}"]
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for url in urls_to_try:
                try:
                    async with session.get(url, allow_redirects=True) as response:
                        results['accessible'] = True
                        results['status_code'] = response.status
                        results['final_url'] = str(response.url)
                        results['has_ssl'] = str(response.url).startswith('https://')
                        results['redirects'] = len(response.history)
                        return results
                except aiohttp.ClientError:
                    continue
                except asyncio.TimeoutError:
                    continue
                    
        return results
    
    async def check_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        ssl_info = {
            'has_ssl': False,
            'valid_ssl': False,
            'issuer': None,
            'expiry_date': None
        }
        
        try:
            context = ssl.create_default_context()
            
            loop = asyncio.get_event_loop()
            
            def get_ssl_info():
                try:
                    with socket.create_connection((domain, 443), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            cert = ssock.getpeercert()
                            return cert
                except Exception:
                    return None
            
            cert = await loop.run_in_executor(None, get_ssl_info)
            
            if cert:
                ssl_info['has_ssl'] = True
                ssl_info['valid_ssl'] = True
                ssl_info['issuer'] = cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
                ssl_info['expiry_date'] = cert.get('notAfter')
                
        except Exception:
            pass
            
        return ssl_info