import aiohttp
import asyncio
import csv
import io
from typing import List, Set, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DomainListsManager:
    def __init__(self):
        self.disposable_sources = [
            "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/domains.txt",
            "https://raw.githubusercontent.com/FGRibreau/mailchecker/master/list.txt",
            "https://raw.githubusercontent.com/wesbos/burner-email-providers/master/emails.txt",
            "https://raw.githubusercontent.com/7c/fakefilter/main/txt/data.txt"
        ]
        
        self.public_providers = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "live.com",
            "mail.ru", "yandex.ru", "yandex.com", "aol.com", "icloud.com",
            "protonmail.com", "zoho.com", "fastmail.com", "gmx.com", "web.de",
            "tutanota.com", "mailbox.org", "hushmail.com", "lycos.com"
        ]
        
        self.disposable_domains: Set[str] = set()
        self.public_provider_domains: Set[str] = set(self.public_providers)
        
    async def update_disposable_lists(self) -> Dict[str, int]:
        results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            tasks = []
            for source in self.disposable_sources:
                task = self._fetch_domain_list(session, source)
                tasks.append(task)
            
            list_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(list_results):
                source = self.disposable_sources[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {source}: {result}")
                    results[source] = 0
                else:
                    results[source] = len(result)
                    self.disposable_domains.update(result)
        
        # Load HubSpot list if available
        hubspot_domains = await self._load_hubspot_list()
        if hubspot_domains:
            results["hubspot_list"] = len(hubspot_domains)
            self.public_provider_domains.update(hubspot_domains)
        
        logger.info(f"Updated domain lists: {len(self.disposable_domains)} disposable, {len(self.public_provider_domains)} public providers")
        return results
    
    async def _fetch_domain_list(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    domains = []
                    for line in content.strip().split('\n'):
                        domain = line.strip().lower()
                        if domain and not domain.startswith('#') and '.' in domain:
                            domains.append(domain)
                    return domains
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return []
    
    async def _load_hubspot_list(self) -> List[str]:
        try:
            # Load the HubSpot CSV file
            with open('PUBLIC_EMAIL_DOMAINS.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                domains = []
                for row in reader:
                    if row and len(row) > 0:
                        domain = row[0].strip().lower()
                        if domain and '.' in domain:
                            domains.append(domain)
                return domains
        except FileNotFoundError:
            logger.warning("HubSpot PUBLIC_EMAIL_DOMAINS.csv not found")
            return []
        except Exception as e:
            logger.error(f"Error loading HubSpot list: {e}")
            return []
    
    def is_disposable_domain(self, domain: str) -> bool:
        return domain.lower() in self.disposable_domains
    
    def is_public_provider(self, domain: str) -> bool:
        return domain.lower() in self.public_provider_domains
    
    def get_domain_category(self, domain: str) -> str:
        domain = domain.lower()
        
        if domain in self.disposable_domains:
            return "disposable"
        elif domain in self.public_provider_domains:
            return "public_provider"
        else:
            return "unknown"
    
    async def initialize(self):
        await self.update_disposable_lists()