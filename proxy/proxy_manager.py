import aiohttp
import asyncio
import random
from typing import List,Optional
from utils.logger import get_logger

proxy_logger = get_logger("Proxy")

class ProxyManager:
    def __init__(self,protocol: str = "http",timeout: int = 5):
        self.protocol = protocol
        self.timeout = timeout
        self.proxies: List[str] = []
        # Free proxies are very unreliable. Replace 'api.proxyscrape' with your personal proxy API key for better results.
        self.api_urls = [
            f"https://api.proxyscrape.com/v2/?request=getproxies&protocol={protocol}&timeout={timeout * 1000}&country=all",
        ]

    #get proxies from ProxyScraper api.
    async def fetch_proxies(self) -> bool:
        for api_url in self.api_urls:
            try :
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url,timeout=20) as response:
                        if response.status == 200:
                            text = await response.text()
                            self.proxies = [line.strip() for line in text.splitlines() if line.strip() and ':' in line]
                            proxy_logger.info(f"fetched {len(self.proxies)} {self.protocol} proxys from {api_url}")
                            return True
                        proxy_logger.warning(f"Failed to fetch proxies from {api_url}, status: {response.status}")
            except Exception as e:
                proxy_logger.warning(f"Proxy fetch error from {api_url}: {e}")
                return False

    #test if the proxy is working.
    async def validate_proxy(self, proxy: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://httpbin.org/ip", proxy=proxy, timeout=self.timeout) as response:
                    if response.status == 200:
                        proxy_logger.debug(f"valid proxy : {proxy}")
                        return True
        except Exception as e:
            proxy_logger.warning(f"proxy validation faild for {proxy} : {e}")
            return False
        return False
    #return random proxy in usable format.
    async def get_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return f"{self.protocol}://{proxy}"

    #Return a validated proxy, trying up to _ times.
    async def get_working_proxy(self) -> Optional[str]:
        for _ in range(5):  # Retry fetching _ times
            if not self.proxies:
                if not await self.fetch_proxies():
                    await asyncio.sleep(3)
                    continue
            for _ in range(10):  # Try _ proxies
                proxy = await self.get_proxy()
                proxy_logger.debug(f"Testing proxy: {proxy}")
                if not proxy:
                    break
                if await self.validate_proxy(proxy):
                    proxy_logger.info(f"Found working proxy: {proxy}")
                    return proxy
                self.proxies.remove(proxy.replace(f"{self.protocol}://", ""))
            proxy_logger.debug("No valid proxies in batch, retrying fetch")
            await asyncio.sleep(3)
        proxy_logger.warning("No working proxies found, proceeding without proxy")
        return None

    #refresh proxies every (interval in secs)
    async def refresh_proxies(self, interval: int = 300) -> None:
        while True:
            await self.fetch_proxies()
            await asyncio.sleep(interval)

