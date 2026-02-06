from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tavily import TavilyClient
from src.core.config import settings

class SearchTool:
    def __init__(self):
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not set in environment variables")
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self.executor = ThreadPoolExecutor(max_workers=5)

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
        异步执行搜索 (运行在线程池中)
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.search_sync, 
            query, 
            max_results
        )

# Singleton instance
search_tool = SearchTool()
