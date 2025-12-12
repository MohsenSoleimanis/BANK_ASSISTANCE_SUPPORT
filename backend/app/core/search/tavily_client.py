"""
Tavily Search Client
Handles web search queries via Tavily API
"""
from tavily import TavilyClient
from typing import List, Dict, Optional
from app.config import settings
from app.utils.logger import get_logger
from app.utils.cache import cache_result

logger = get_logger(__name__)


class TavilySearchClient:
    """Client for Tavily web search API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily client"""
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key)
        self.max_results = settings.TAVILY_MAX_RESULTS
    
    @cache_result(ttl=settings.SEARCH_CACHE_TTL)
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search the web using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: 'basic' or 'advanced'
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            
        Returns:
            List of search results with title, url, content, score
        """
        try:
            max_results = max_results or self.max_results
            
            logger.info(f"Searching Tavily: '{query}'")
            
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            results = response.get("results", [])
            logger.info(f"Found {len(results)} results")
            
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0)
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching Tavily: {str(e)}")
            return []
    
    async def search_banking_info(
        self,
        query: str,
        bank_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for banking-specific information
        Returns ALL results - let the LLM decide what's relevant
        
        Args:
            query: Search query
            bank_name: Specific bank to search for
            
        Returns:
            Search results
        """
        # Enhance query for banking context
        enhanced_query = query
        if bank_name:
            enhanced_query = f"{bank_name} {query}"
        
        # Just do a regular search - don't filter aggressively
        results = await self.search(
            query=enhanced_query,
            search_depth="basic",
            max_results=self.max_results
        )
        
        # Return all results with content
        # Filter only results that have actual content
        return [r for r in results if r.get("content") and len(r["content"]) > 50]
    
    async def get_current_rates(self, bank_name: Optional[str] = None) -> List[Dict]:
        """Get current interest rates"""
        query = "current interest rates savings checking 2024"
        if bank_name:
            query = f"{bank_name} {query}"
        
        return await self.search(query, search_depth="advanced")
    
    async def search_regulations(self, topic: str) -> List[Dict]:
        """Search for banking regulations"""
        query = f"banking regulations {topic} fdic federal reserve"
        
        return await self.search(
            query=query,
            search_depth="advanced",
            include_domains=["fdic.gov", "federalreserve.gov", "occ.gov"]
        )


# Global client instance
tavily_client = TavilySearchClient()