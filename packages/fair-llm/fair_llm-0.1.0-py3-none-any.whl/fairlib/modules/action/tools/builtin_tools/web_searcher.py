import hashlib
import json
import threading
import requests
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
from fairlib.core.prompts import DateContextMixin

from fairlib.core.interfaces.tools import AbstractTool

# Configure logging
logger = logging.getLogger(__name__)


class SearchProvider(ABC):
    """Base class for search providers"""
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass


class GooglePSEProvider(SearchProvider):
    """Google Programmable Search Engine provider using sync requests"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 WebSearcherTool/1.0'})
        
    @property
    def name(self) -> str:
        return "Google PSE"
    
    def search(self, query: str, count: int = 10, **kwargs) -> List[Dict[str, Any]]:
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(count, 10),
            "safe": kwargs.get("safe_search", "active"),
        }
        
        # Add optional parameters
        if kwargs.get("date_restrict"):
            params["dateRestrict"] = kwargs["date_restrict"]
        if kwargs.get("site"):
            params["siteSearch"] = kwargs["site"]
            params["siteSearchFilter"] = "i"
            
        try:
            response = self.session.get(
                self.base_url, 
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return self._parse_results(response.json(), query)
            elif response.status_code == 429:
                raise Exception("Google PSE rate limit exceeded")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"Google PSE search failed: {error_msg}")
                
        except requests.Timeout:
            raise Exception("Google PSE search timed out")
        except requests.RequestException as e:
            raise Exception(f"Network error during Google PSE search: {str(e)}")
    
    def _parse_results(self, data: Dict, query: str) -> List[Dict[str, Any]]:
        results = []
        search_info = data.get("searchInformation", {})
        total_results = search_info.get("totalResults", "0")
        
        for item in data.get("items", []):
            result = {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "display_url": item.get("displayLink", ""),
                "snippet": item.get("snippet", ""),
                "source": "Google",
                "total_results": total_results,
                "original_query": query
            }
            
            # Extract metadata from pagemap if available
            if "pagemap" in item:
                pagemap = item["pagemap"]
                if "metatags" in pagemap and pagemap["metatags"]:
                    metatags = pagemap["metatags"][0]
                    result["date_published"] = (
                        metatags.get("article:published_time") or
                        metatags.get("published_time") or
                        metatags.get("publication_date")
                    )
                    result["author"] = metatags.get("author")
                    result["description"] = metatags.get("og:description")
            
            results.append(result)
        
        return results

class SearchCache:
    """Thread-safe in-memory cache for search results"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_size = max_size
        self._lock = threading.RLock()
    
    def get(self, query: str) -> Optional[List[Dict]]:
        with self._lock:
            key = self._get_cache_key(query)
            if key in self.cache:
                entry, timestamp = self.cache[key]
                if datetime.now() - timestamp < self.ttl:
                    logger.debug(f"Cache hit for query: {query[:50]}...")
                    return entry
                else:
                    del self.cache[key]
            return None
    
    def set(self, query: str, results: List[Dict]):
        with self._lock:
            key = self._get_cache_key(query)
            self.cache[key] = (results, datetime.now())
            
            # Implement LRU eviction if cache is too large
            if len(self.cache) > self.max_size:
                # Remove oldest entries
                sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
                for old_key, _ in sorted_items[:100]:
                    del self.cache[old_key]
    
    def _get_cache_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()


class SearchType(Enum):
    GENERAL = "general"
    NEWS = "news"
    ACADEMIC = "academic"
    CODE = "code"
    FINANCIAL = "financial"


class WebSearcherTool(AbstractTool):
    """
    A robust web searching tool that works reliably in any execution context.
    Uses synchronous HTTP requests to avoid event loop issues while maintaining
    high performance through connection pooling and caching.
    """
    
    name = "web_searcher"
    description = (
        "Searches the web for up-to-date information on a given topic."
    )
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = SearchCache(
            ttl_seconds=config.get("cache_ttl", 3600),
            max_size=config.get("cache_max_size", 1000)
        )
        self.max_results = config.get("max_results", 10)
        self.providers = self._initialize_providers()
        self.date_context_mix = DateContextMixin()
        
    def _initialize_providers(self) -> List[SearchProvider]:
        """Initialize search providers based on configuration"""
        providers = []
        
        if "google_api_key" in self.config and "google_search_engine_id" in self.config:
            try:
                provider = GooglePSEProvider(
                    self.config["google_api_key"],
                    self.config["google_search_engine_id"]
                )
                providers.append(provider)
                logger.info("Initialized Google PSE provider")
            except Exception as e:
                logger.error(f"Failed to initialize Google PSE: {e}")
                
        if not providers:
            raise ValueError("No search providers could be initialized")
            
        return providers
    
    def use(self, tool_input: str, search_type: str = "general", extract_content: bool = False) -> str:
        """
        Performs a web search with the given query.
        
        Args:
            tool_input: The search query
            search_type: Type of search (general, news, academic, etc.)
            extract_content: Whether to extract full content (not implemented in sync version)
            
        Returns:
            JSON string with search results
        """
        try:
            # First, add context to current date/time
            tool_input = self.date_context_mix.enhance_with_date(tool_input)

            # Check cache first
            cached = self.cache.get(tool_input)
            if cached:
                return json.dumps({
                    "results": cached, 
                    "from_cache": True,
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            
            # Enhance query based on type and content
            enhanced_query = self._enhance_query(tool_input, search_type)
            logger.info(f"Searching for: {enhanced_query[:100]}...")
            
            # Try each provider until one succeeds
            results = None
            errors = []
            
            for provider in self.providers:
                try:
                    logger.info(f"Trying provider: {provider.name}")
                    results = provider.search(enhanced_query, count=self.max_results)
                    
                    if results:
                        print(f"Got {len(results)} results from {provider.name}")
                        break
                        
                except Exception as e:
                    error_msg = f"{provider.name}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
            
            if not results:
                logger.error(f"All providers failed. Errors: {errors}")
                return json.dumps({
                    "error": "All search providers failed",
                    "details": errors,
                    "query": tool_input
                }, indent=2)
            
            # Rank and process results
            ranked_results = self._rank_results(results, tool_input)
            
            # Cache successful results
            self.cache.set(tool_input, ranked_results)
            
            return json.dumps({
                "query": tool_input,
                "enhanced_query": enhanced_query,
                "search_type": search_type,
                "results": ranked_results,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Unexpected error in search: {str(e)}", exc_info=True)
            return json.dumps({
                "error": "Search failed",
                "details": str(e),
                "query": tool_input
            }, indent=2)
    
    def _enhance_query(self, query: str, search_type: str) -> str:
        """Enhance query based on search type and content analysis"""
        
        # Base enhancements by search type
        enhancements = {
            SearchType.NEWS.value: f"{query} news {datetime.now().year}",
            SearchType.ACADEMIC.value: f"{query} research paper scholarly",
            SearchType.CODE.value: f"{query} programming code example",
            SearchType.FINANCIAL.value: f"{query} finance market data"
        }
        
        enhanced = enhancements.get(search_type, query)
        
        # Additional enhancements for specific topics
        query_lower = query.lower()
        
        # Time-based queries
        if "past" in query_lower or "last" in query_lower:
            import re
            years_match = re.search(r'(\d+)\s*years?', query_lower)
            if years_match:
                years = int(years_match.group(1))
                enhanced += f" {datetime.now().year - years}-{datetime.now().year}"
        
        return enhanced
    
    def _rank_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """Rank results based on relevance, authority, and freshness"""
        query_terms = set(original_query.lower().split())
        
        for result in results:
            score = 0

            # Text relevance scoring
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            
            # Term frequency
            for term in query_terms:
                score += text.count(term) * 2
            
            # Exact phrase match bonus
            if original_query.lower() in text:
                score += 20
            
            # URL/domain quality scoring
            url = result.get("url", "").lower()
            trusted_domains = {
                "nasa.gov": 20,
                "noaa.gov": 20,
                "climate.gov": 18,
                "nature.com": 15,
                "science.org": 15,
                "arxiv.org": 12,
                "github.com": 10,
                "stackoverflow.com": 8,
                ".org": 4
            }
            
            for domain, bonus in trusted_domains.items():
                if domain in url:
                    score += bonus
                    break
            
            # Data source indicators
            if any(indicator in text for indicator in ["download", "csv", "api", "dataset"]):
                score += 10
            
            result["relevance_score"] = score
        
        # Sort by relevance score
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)