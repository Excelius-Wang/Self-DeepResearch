from typing import List, Dict, Any
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from tavily import TavilyClient
from src.core.config import settings

class SearchTool:
    def __init__(self):
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not set in environment variables")
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self.executor = ThreadPoolExecutor(max_workers=5)
        # Simple in-memory cache to avoid repeated searches
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate a cache key for the query"""
        return hashlib.md5(f"{query}:{max_results}".encode()).hexdigest()

    def search_sync(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        同步执行搜索
        """
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_raw_content=False,
                include_answer=False
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        异步执行搜索 (运行在线程池中)，带缓存支持
        """
        cache_key = self._get_cache_key(query, max_results)

        # Check cache first
        if cache_key in self._cache:
            print(f"--- [Search] Cache hit for: {query} ---")
            return self._cache[cache_key]

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            self.executor,
            self.search_sync,
            query,
            max_results
        )

        # Store in cache
        self._cache[cache_key] = results
        return results

    def clear_cache(self):
        """Clear the search cache"""
        self._cache.clear()

# Singleton instance
search_tool = SearchTool()
