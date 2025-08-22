import json
import logging
import re
import requests
from typing import List, Dict, Any, Optional, Union, Tuple
from pydantic import BaseModel, Field, ValidationError
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO, BytesIO
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from datetime import datetime
import PyPDF2
from urllib.parse import urlunparse

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.interfaces.tools import AbstractTool
from fairlib.core.prompts import DateContextMixin
from fairlib import Message

logger = logging.getLogger(__name__)


class ExtractedData(BaseModel):
    """Standard format for extracted data"""
    source_url: str = Field(..., description="URL where data was extracted from")
    data_type: str = Field(..., description="Type of data (table, time_series, etc.)")
    columns: List[str] = Field(..., description="Column names of the extracted data")
    rows: List[List[Any]] = Field(..., description="Rows of data as lists of values")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    extraction_method: str = Field(..., description="Method used to extract data")
    confidence_score: float = Field(default=1.0, description="Confidence in extraction quality")

class URLCleaner:
    """Comprehensive URL cleaning utilities"""
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Clean URL by removing trailing punctuation and artifacts"""
        if not url:
            return url
            
        # Remove surrounding quotes
        url = url.strip('"\'')
        
        # Remove trailing punctuation that's definitely not part of URL
        # But preserve query parameters that might end with punctuation
        if '?' in url:
            base, params = url.split('?', 1)
            base = base.rstrip(';:,.')
            url = f"{base}?{params}"
        else:
            url = url.rstrip(';:,.')
        
        # Fix common artifacts
        url = re.sub(r'/;$', '/', url)  # Remove /; at end
        url = re.sub(r';\s*$', '', url)  # Remove trailing semicolon with whitespace
        url = re.sub(r',\s*$', '', url)  # Remove trailing comma with whitespace
        
        # URL decode if needed
        try:
            from urllib.parse import unquote
            url = unquote(url)
        except:
            pass
        
        # Validate and normalize
        try:
            parsed = urlparse(url)
            # Ensure scheme
            if not parsed.scheme:
                url = 'https://' + url
                parsed = urlparse(url)
            # Reconstruct
            url = urlunparse(parsed)
        except:
            logger.warning(f"Could not parse URL: {url}")
        
        return url
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """Extract and clean URLs from text"""
        # More precise regex that stops at common delimiters
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?=[;\s,.]|$)'
        urls = re.findall(url_pattern, text)
        
        # Clean each URL
        cleaned_urls = []
        for url in urls:
            cleaned = URLCleaner.clean_url(url)
            if cleaned and cleaned not in cleaned_urls:
                cleaned_urls.append(cleaned)
        
        return cleaned_urls


class ContentFetcher:
    """Fetches content from URLs with proper error handling"""
    
    def __init__(self, timeout: int = 15, max_size: int = 10 * 1024 * 1024):  # 10MB max
        self.timeout = timeout
        self.max_size = max_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, url: str) -> Tuple[Optional[bytes], Optional[str], Dict[str, Any]]:
        """
        Fetch content from URL
        Returns: (content_bytes, content_type, metadata)
        """
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check content size
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > self.max_size:
                raise ValueError(f"Content too large: {content_length} bytes")
            
            # Read content in chunks to respect max_size
            content = BytesIO()
            size = 0
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
                if size > self.max_size:
                    raise ValueError(f"Content too large: >{self.max_size} bytes")
                content.write(chunk)
            
            content_bytes = content.getvalue()
            content_type = response.headers.get('Content-Type', '').lower()
            
            metadata = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'encoding': response.encoding,
                'url': response.url
            }
            
            return content_bytes, content_type, metadata
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None, None, {'error': str(e)}


class GenericAPIConstructor:
    """Constructs API endpoints from documentation for ANY type of API"""
    
    def __init__(self, llm: AbstractChatModel):
        self.llm = llm
    
    def analyze_and_construct_url(self, base_url: str, extracted_content: Dict[str, Any], 
                                 user_context: str) -> Optional[Dict[str, Any]]:
        """
        Analyze extracted content and construct appropriate data retrieval strategy
        """
        
        # First, determine what type of content we have
        content_type = self._identify_content_type(extracted_content)
        
        if content_type == "api_documentation":
            return self._handle_api_documentation(base_url, extracted_content, user_context)
        elif content_type == "data_portal":
            return self._handle_data_portal(extracted_content, user_context)
        elif content_type == "form_interface":
            return self._handle_form_interface(base_url, extracted_content, user_context)
        else:
            return None
    
    def _identify_content_type(self, content: Dict[str, Any]) -> str:
        """Identify what type of content we're dealing with"""
        
        # Check if it's API documentation
        if self._looks_like_api_docs(content):
            return "api_documentation"
        
        # Check if it's a data portal with download links
        if self._has_download_indicators(content):
            return "data_portal"
        
        # Check if it's a form-based interface
        if self._looks_like_form_params(content):
            return "form_interface"
        
        return "unknown"
    
    def _looks_like_api_docs(self, content: Dict[str, Any]) -> bool:
        """Check if content appears to be API documentation"""
        
        # Look for common API documentation patterns
        api_indicators = [
            'parameter', 'endpoint', 'request', 'response', 'format',
            'api', 'method', 'authorization', 'query', 'param'
        ]
        
        if 'columns' in content and content['columns']:
            columns_text = ' '.join(str(col).lower() for col in content['columns'])
            if 'rows' in content and content['rows']:
                rows_text = ' '.join(str(item).lower() for row in content['rows'][:5] for item in row)
                combined_text = columns_text + ' ' + rows_text
                
                matches = sum(1 for indicator in api_indicators if indicator in combined_text)
                return matches >= 2
        
        return False
    
    def _has_download_indicators(self, content: Dict[str, Any]) -> bool:
        """Check if content has download links or buttons"""
        
        download_indicators = ['download', 'export', 'csv', 'json', 'excel', 'pdf', 'get data']
        
        # Check in any string content
        content_str = json.dumps(content).lower()
        return any(indicator in content_str for indicator in download_indicators)
    
    def _looks_like_form_params(self, content: Dict[str, Any]) -> bool:
        """Check if content appears to be form parameters"""
        
        form_indicators = ['select', 'choose', 'option', 'dropdown', 'checkbox', 'input']
        
        content_str = json.dumps(content).lower()
        return any(indicator in content_str for indicator in form_indicators)
    
    def _handle_api_documentation(self, base_url: str, content: Dict[str, Any], 
                                 user_context: str) -> Optional[Dict[str, Any]]:
        """Handle API documentation to construct valid API calls"""
        
        prompt = f"""
Analyze this API documentation and construct a valid API URL to fetch data.

User's Request: {user_context}

Base URL: {base_url}

Documentation Content:
{json.dumps(content, indent=2)}

Instructions:
1. Identify the required and optional parameters
2. Based on the user's request, determine appropriate values for each parameter
3. Construct a complete, valid API URL
4. If there are example values or formats shown, use them as guidance

Output a JSON object with:
{{
    "url": "complete API URL",
    "method": "GET or POST",
    "headers": {{}},  // if any special headers needed
    "explanation": "brief explanation of parameter choices"
}}
"""
        
        try:
            response = self.llm.chat([Message(role="system", content=prompt)])
            response = _strip_code_fences(response)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to construct API URL: {e}")
            return None
    
    def _handle_data_portal(self, content: Dict[str, Any], user_context: str) -> Optional[Dict[str, Any]]:
        """Handle data portal pages with multiple download options"""
        
        prompt = f"""
Analyze this data portal content and identify the best data source to download.

User's Request: {user_context}

Available Content:
{json.dumps(content, indent=2)}

Instructions:
1. Identify available data files or links
2. Choose the most relevant one based on the user's request
3. Prefer machine-readable formats (CSV, JSON) over PDFs
4. If multiple options exist, choose the most comprehensive one

Output a JSON object with:
{{
    "download_urls": ["url1", "url2"],  // in order of preference
    "format": "csv/json/excel",
    "explanation": "why these files were chosen"
}}
"""
        
        try:
            response = self.llm.chat([Message(role="system", content=prompt)])
            response = _strip_code_fences(response)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to identify download links: {e}")
            return None
    
    def _handle_form_interface(self, base_url: str, content: Dict[str, Any], 
                              user_context: str) -> Optional[Dict[str, Any]]:
        """Handle form-based interfaces"""
        
        prompt = f"""
This appears to be a form-based data interface. Construct the appropriate form submission.

User's Request: {user_context}

Form Elements Found:
{json.dumps(content, indent=2)}

Base URL: {base_url}

Instructions:
1. Identify form fields and their possible values
2. Based on the user's request, fill in appropriate values
3. Construct either a GET URL with parameters or POST data

Output a JSON object with:
{{
    "url": "form submission URL",
    "method": "GET or POST",
    "params": {{}},  // for GET
    "data": {{}},    // for POST
    "explanation": "form field choices"
}}
"""
        
        try:
            response = self.llm.chat([Message(role="system", content=prompt)])
            response = _strip_code_fences(response)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to construct form submission: {e}")
            return None
        

class HTMLDataParser:
    """Extracts structured data from HTML pages"""
    
    def extract_tables(self, html: str, url: str) -> List[ExtractedData]:
        """Extract all tables from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        extracted_data = []
        
        # Find all tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            try:
                # Use pandas to parse HTML table
                df = pd.read_html(StringIO(str(table)))[0]
                
                # Clean column names
                if df.columns.nlevels > 1:
                    df.columns = [' '.join(col).strip() for col in df.columns.values]
                else:
                    df.columns = [str(col).strip() for col in df.columns]
                
                # Convert to our format
                extracted = ExtractedData(
                    source_url=url,
                    data_type="table",
                    columns=df.columns.tolist(),
                    rows=df.values.tolist(),
                    metadata={
                        'table_index': i,
                        'shape': df.shape,
                        'extraction_time': datetime.now().isoformat()
                    },
                    extraction_method="html_table_parser",
                    confidence_score=0.9 # TODO:: make this dyanmic! curently just static assignment
                )
                extracted_data.append(extracted)
                
            except Exception as e:
                logger.warning(f"Failed to parse table {i} from {url}: {e}")
        
        return extracted_data
    
    def extract_structured_lists(self, html: str, url: str) -> List[ExtractedData]:
        """Extract structured data from lists and definition lists"""
        soup = BeautifulSoup(html, 'html.parser')
        extracted_data = []
        
        # Look for definition lists (often used for key-value data)
        for dl in soup.find_all('dl'):
            terms = [dt.get_text(strip=True) for dt in dl.find_all('dt')]
            definitions = [dd.get_text(strip=True) for dd in dl.find_all('dd')]
            
            if terms and definitions:
                data = ExtractedData(
                    source_url=url,
                    data_type="definition_list",
                    columns=["term", "definition"],
                    rows=[[t, d] for t, d in zip(terms, definitions)],
                    metadata={'list_type': 'dl'},
                    extraction_method="html_list_parser",
                    confidence_score=0.8 # TODO:: make this dyanmic! curently just static assignment
                )
                extracted_data.append(data)
        
        return extracted_data


class CSVDataParser:
    """Handles CSV data from URLs or embedded in pages"""
    
    def parse_csv_url(self, content: bytes, url: str, encoding: str = 'utf-8') -> Optional[ExtractedData]:
        """Parse CSV content"""
        try:
            # Try to decode content
            text = content.decode(encoding)
            
            # Use pandas to parse CSV
            df = pd.read_csv(StringIO(text))
            
            # Handle common CSV issues
            df = df.dropna(how='all')  # Remove empty rows
            df.columns = [str(col).strip() for col in df.columns]  # Clean column names
            
            return ExtractedData(
                source_url=url,
                data_type="csv",
                columns=df.columns.tolist(),
                rows=df.values.tolist(),
                metadata={
                    'shape': df.shape,
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'encoding': encoding
                },
                extraction_method="csv_parser",
                confidence_score=0.95
            )
            
        except Exception as e:
            logger.error(f"Failed to parse CSV from {url}: {e}")
            return None


class JSONDataParser:
    """Handles JSON and API responses"""
    
    def parse_json(self, content: bytes, url: str) -> Optional[ExtractedData]:
        """Parse JSON content into tabular format"""
        try:
            data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON structures
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # Array of objects - common API response
                df = pd.DataFrame(data)
                return ExtractedData(
                    source_url=url,
                    data_type="json_array",
                    columns=df.columns.tolist(),
                    rows=df.values.tolist(),
                    metadata={'original_length': len(data)},
                    extraction_method="json_parser",
                    confidence_score=0.95
                )
            
            elif isinstance(data, dict):
                # Check for specific data structures
                
                # Handle nested data arrays
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        if isinstance(value[0], (dict, list)):
                            df = pd.DataFrame(value)
                            return ExtractedData(
                                source_url=url,
                                data_type="json_nested",
                                columns=df.columns.tolist(),
                                rows=df.values.tolist(),
                                metadata={'data_key': key},
                                extraction_method="json_parser",
                                confidence_score=0.9
                            )
                
                # Handle time series data (e.g., {"dates": [...], "values": [...]})
                keys = list(data.keys())
                if len(keys) >= 2 and all(isinstance(data[k], list) for k in keys):
                    # Try to create a table from parallel arrays
                    first_key = keys[0]
                    if len(set(len(data[k]) for k in keys)) == 1:  # All arrays same length
                        rows = []
                        for i in range(len(data[first_key])):
                            row = [data[k][i] for k in keys]
                            rows.append(row)
                        
                        return ExtractedData(
                            source_url=url,
                            data_type="json_parallel_arrays",
                            columns=keys,
                            rows=rows,
                            metadata={'structure': 'parallel_arrays'},
                            extraction_method="json_parser",
                            confidence_score=0.85
                        )
            
            # Fallback: flatten the JSON
            flattened = pd.json_normalize(data)
            return ExtractedData(
                source_url=url,
                data_type="json_flattened",
                columns=flattened.columns.tolist(),
                rows=flattened.values.tolist(),
                metadata={'structure': 'flattened'},
                extraction_method="json_parser",
                confidence_score=0.8
            )
            
        except Exception as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            return None


class LLMDataExtractor:
    """Uses LLM to extract structured data from unstructured text"""
    
    def __init__(self, llm: AbstractChatModel):
        self.llm = llm
    
    def extract_from_text(self, text: str, context: str, url: str) -> Optional[ExtractedData]:
        """Use LLM to extract ANY type of structured data from text"""
        
        # Dynamically create extraction instructions based on context
        prompt = f"""
You are a data extraction expert. Analyze the following text and extract structured data.

Context about what we're looking for: {context}

Instructions:
1. Identify what type of data is present (time series, categorical, numerical, etc.)
2. Extract the actual data values, not descriptions
3. Create appropriate column names based on the data you find
4. Output ONLY valid JSON with 'columns' and 'rows' fields
5. Include units in column names when applicable (e.g., 'temperature_celsius', 'price_usd')

Examples of good extraction:
- Time series: columns=['date', 'value', 'unit'], rows=[['2020', '15.2', 'C'], ...]
- Comparison data: columns=['item', 'metric1', 'metric2'], rows=[['A', '10', '20'], ...]
- Single metrics: columns=['metric', 'value', 'unit'], rows=[['speed', '100', 'mph'], ...]

Text to analyze:
{text}

Output JSON:
"""
        
        try:
            response = self.llm.chat([Message(role="system", content=prompt)])
            response = _strip_code_fences(response)
            data = json.loads(response)
            
            # Validate the response has required fields
            if 'columns' not in data or 'rows' not in data:
                logger.error("LLM response missing required fields")
                return None
            
            # Auto-detect data type based on columns
            data_type = self._infer_data_type(data['columns'])
            
            return ExtractedData(
                source_url=url,
                data_type=data_type,
                columns=data['columns'],
                rows=data['rows'],
                metadata={
                    'context': context[:200],
                    'text_length': len(text),
                    'inferred_type': data_type
                },
                extraction_method="llm_extraction",
                confidence_score=0.7
            )
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return None
    
    def _infer_data_type(self, columns: List[str]) -> str:
        """Infer the type of data based on column names"""
        columns_lower = [col.lower() for col in columns]
        
        # Check for common patterns
        if any(term in ' '.join(columns_lower) for term in ['date', 'time', 'year', 'month']):
            return "time_series"
        elif any(term in ' '.join(columns_lower) for term in ['category', 'type', 'class']):
            return "categorical"
        elif any(term in ' '.join(columns_lower) for term in ['price', 'cost', 'value', 'amount']):
            return "financial"
        elif len(columns) == 2:
            return "key_value_pairs"
        else:
            return "general_data"


class WebDataExtractor(AbstractTool):
    """
    A generic data extractor that works with any type of web data source.
    Uses intelligent multi-strategy approach to extract actual data values.
    """
    
    name = "web_data_extractor"
    description = (
        "Extracts structured data from ANY web source. Handles APIs, downloads, "
        "forms, tables, and documents. Automatically adapts extraction strategy "
        "based on the content type and user's needs."
    )
    
    def __init__(self, llm: AbstractChatModel, output_model: BaseModel = ExtractedData):
        self.llm = llm
        self.output_model = output_model
        self.content_fetcher = ContentFetcher()
        self.html_parser = HTMLDataParser()
        self.csv_parser = CSVDataParser()
        self.json_parser = JSONDataParser()
        self.llm_extractor = LLMDataExtractor(llm)
        self.api_constructor = GenericAPIConstructor(llm)
        self.date_context = DateContextMixin()
    
    def use(self, tool_input: str) -> str:
        """
        Extract data using intelligent strategy selection
        """
        try:
            # Parse input to get URLs and context
            input_data = self._parse_input(tool_input)
            
            all_extracted_data = []
            strategies_tried = []
            
            for url_info in input_data['urls']:
                url = url_info['url']
                context = url_info.get('context', input_data.get('context', ''))
                
                logger.info(f"Processing URL: {url}")
                
                # Try intelligent extraction
                extracted, strategies = self._intelligent_extract(url, context, tool_input)
                
                strategies_tried.extend(strategies)
                
                if extracted:
                    all_extracted_data.extend(extracted)
                else:
                    # If all strategies failed, add to errors
                    strategies_tried.append(f"Failed to extract from {url}")
            
            return self._format_results(all_extracted_data, strategies_tried)
            
        except Exception as e:
            logger.error(f"WebDataExtractor error: {e}", exc_info=True)
            return json.dumps({"error": f"Data extraction failed: {str(e)}"})
    
    def _parse_input(self, tool_input: str) -> Dict[str, Any]:
        """Parse input and preserve full context"""
        result = {
            'urls': [],
            'context': '',
            'original_query': '',
            'task_description': ''
        }
        
        # Try JSON parsing first
        try:
            data = json.loads(tool_input)
            
            # From Researcher results
            if 'results' in data:
                result['original_query'] = data.get('query', '')
                
                for r in data['results']:
                    if 'url' in r:
                        cleaned_url = URLCleaner.clean_url(r['url'])
                        result['urls'].append({
                            'url': cleaned_url,
                            'title': r.get('title', ''),
                            'snippet': r.get('snippet', ''),
                            'context': f"{r.get('title', '')} - {r.get('snippet', '')}"
                        })
                
                result['context'] = result['original_query']
            
            # Direct URL input
            elif 'url' in data:
                result['urls'] = [{'url': URLCleaner.clean_url(data['url'])}]
                result['context'] = data.get('context', '')
            
            else:
                # Plain text input - extract URLs and preserve context
                raise json.JSONDecodeError("Not JSON", "", 0)
                
        except json.JSONDecodeError:
            # Parse as text
            urls = URLCleaner.extract_urls_from_text(tool_input)
            
            # Extract task description (everything that's not a URL)
            task_text = tool_input
            for url in urls:
                task_text = task_text.replace(url, '')
            task_text = task_text.strip(' -;:,.')
            
            result['urls'] = [{'url': url} for url in urls]
            result['task_description'] = task_text
            result['context'] = task_text
            result['original_query'] = tool_input
        
        # Add date context
        date_info = self.date_context.get_current_date_context()
        result['date_context'] = date_info
        
        return result
    
    def _intelligent_extract(self, url: str, context: str, original_input: str) -> Tuple[List[ExtractedData], List[str]]:
        """
        Use intelligent strategy selection based on content analysis
        """
        strategies_tried = []
        
        # Strategy 1: Direct fetch and analyze
        strategies_tried.append("Direct content fetch")
        content, content_type, metadata = self.content_fetcher.fetch(url)
        
        if not content:
            return [], strategies_tried
        
        # Try direct parsing first
        initial_extract = self._extract_data(url, content, content_type, context)
        
        # Check if we got actual data or just documentation/interface
        if initial_extract and self._contains_actual_data(initial_extract[0]):
            strategies_tried.append("SUCCESS: Found data in initial fetch")
            return initial_extract, strategies_tried
        
        # Strategy 2: Analyze content for next steps
        strategies_tried.append("Analyzing content type")
        
        # Convert first extraction to dict for analysis
        extracted_dict = {}
        if initial_extract:
            extracted_dict = {
                'columns': initial_extract[0].columns,
                'rows': initial_extract[0].rows[:10],  # First 10 rows for analysis
                'metadata': initial_extract[0].metadata
            }
        
        content_analysis = self.api_constructor.analyze_and_construct_url(
            url, 
            extracted_dict,
            context
        )
        
        print("GOT CONSTRUCTED URL FROM LLM: ", content_analysis)

        if content_analysis:
            # Try the suggested approach
            if 'url' in content_analysis:
                strategies_tried.append(f"Trying constructed URL: {content_analysis.get('explanation', '')}")
                
                # Fetch from constructed URL
                new_content, new_type, _ = self.content_fetcher.fetch(content_analysis['url'])
                if new_content:
                    new_extract = self._extract_data(
                        content_analysis['url'], 
                        new_content, 
                        new_type or 'unknown',
                        context
                    )
                    if new_extract:
                        strategies_tried.append("SUCCESS: Got data from constructed URL")
                        return new_extract, strategies_tried
            
            elif 'download_urls' in content_analysis:
                # Try download URLs
                for dl_url in content_analysis['download_urls'][:3]:
                    strategies_tried.append(f"Trying download: {dl_url}")
                    dl_content, dl_type, _ = self.content_fetcher.fetch(dl_url)
                    if dl_content:
                        dl_extract = self._extract_data(dl_url, dl_content, dl_type or '', context)
                        if dl_extract and self._contains_actual_data(dl_extract[0]):
                            strategies_tried.append("SUCCESS: Got data from download")
                            return dl_extract, strategies_tried
        
        # Strategy 3: Look for any links in the page that might be data
        if content:
            strategies_tried.append("Searching for data links in page")
            html_content = content.decode('utf-8', errors='ignore')
            data_links = self._find_potential_data_links(html_content, url)
            
            for link_info in data_links[:5]:  # Try up to 5 links
                strategies_tried.append(f"Trying potential data link: {link_info['text']}")
                link_content, link_type, _ = self.content_fetcher.fetch(link_info['url'])
                if link_content:
                    link_extract = self._extract_data(
                        link_info['url'], 
                        link_content, 
                        link_type or '',
                        context
                    )
                    if link_extract and self._contains_actual_data(link_extract[0]):
                        strategies_tried.append("SUCCESS: Found data in linked file")
                        return link_extract, strategies_tried
        
        # Strategy 4: Use LLM to extract any data from the page
        if content and (not initial_extract or not self._contains_actual_data(initial_extract[0])):
            strategies_tried.append("Using LLM to extract any available data")
            html_content = content.decode('utf-8', errors='ignore')
            llm_extract = self._llm_extract_any_data(html_content, url, context)
            if llm_extract:
                strategies_tried.append("SUCCESS: LLM extracted data from page")
                return [llm_extract], strategies_tried
        
        # Return whatever we got, even if it's just documentation
        strategies_tried.append("Returning best available content")
        return initial_extract or [], strategies_tried
    
    def _extract_data(self, url: str, content: bytes, content_type: str, context: str) -> List[ExtractedData]:
        """Extract data based on content type - GENERAL PURPOSE"""
        extracted_data = []
        
        # Route based on content type
        if 'csv' in content_type or url.endswith('.csv'):
            data = self.csv_parser.parse_csv_url(content, url)
            if data:
                extracted_data.append(data)
        
        elif 'json' in content_type or url.endswith('.json'):
            data = self.json_parser.parse_json(content, url)
            if data:
                extracted_data.append(data)
        
        elif 'html' in content_type or url.endswith('.html') or 'text/html' in content_type:
            html = content.decode('utf-8', errors='ignore')
            
            # Try to extract tables first (most structured)
            tables = self.html_parser.extract_tables(html, url)
            extracted_data.extend(tables)
            
            # Also try structured lists
            lists = self.html_parser.extract_structured_lists(html, url)
            extracted_data.extend(lists)
            
            # If no structured data found, use LLM to intelligently extract
            if not extracted_data:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text(separator=' ', strip=True)
                
                # TODO:: This section needs some refactoring or more testing. Test with a large text block and see
                # what the llm actually pulls out

                # Let LLM figure out what data to extract based on context
                llm_data = self.llm_extractor.extract_from_text(
                    text[:5000],  # Increased limit for better context
                    context,
                    url
                )
                if llm_data:
                    extracted_data.append(llm_data)
        
        # Handle PDF files
        elif 'pdf' in content_type or url.endswith('.pdf'):
            extracted_data.extend(self._extract_from_pdf(content, url, context))
        
        # Handle Excel files
        elif any(url.endswith(ext) for ext in ['.xlsx', '.xls']) or 'spreadsheet' in content_type:
            extracted_data.extend(self._extract_from_excel(content, url))
        
        return extracted_data
    
    def _extract_from_pdf(self, content: bytes, url: str, context: str) -> List[ExtractedData]:
        """Extract data from PDF files"""
        extracted_data = []
        
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Use LLM to extract structured data
            if text.strip():
                llm_data = self.llm_extractor.extract_from_text(
                    text[:5000],  # Limit for LLM context
                    context,
                    url
                )
                if llm_data:
                    llm_data.metadata['source_type'] = 'pdf'
                    llm_data.metadata['page_count'] = len(pdf_reader.pages)
                    extracted_data.append(llm_data)
                    
        except Exception as e:
            logger.error(f"PDF extraction failed for {url}: {e}")
        
        return extracted_data
    
    def _extract_from_excel(self, content: bytes, url: str) -> List[ExtractedData]:
        """Extract data from Excel files"""
        extracted_data = []
        
        try:
            # Read Excel file
            excel_file = BytesIO(content)
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            
            # Process each sheet
            for sheet_name, df in excel_data.items():
                if not df.empty:
                    data = ExtractedData(
                        source_url=url,
                        data_type="excel_sheet",
                        columns=df.columns.tolist(),
                        rows=df.values.tolist(),
                        metadata={
                            'sheet_name': sheet_name,
                            'shape': df.shape,
                            'source_type': 'excel'
                        },
                        extraction_method="excel_parser",
                        confidence_score=0.95
                    )
                    extracted_data.append(data)
                    
        except Exception as e:
            logger.error(f"Excel extraction failed for {url}: {e}")
        
        return extracted_data
    
    def _contains_actual_data(self, extracted: ExtractedData) -> bool:
        """Check if extracted content contains actual data vs just documentation"""
        
        if not extracted.rows:
            return False
        
        # Check for documentation indicators
        doc_indicators = [
            'parameter', 'description', 'type', 'format', 'example',
            'required', 'optional', 'accepted', 'values', 'api'
        ]
        
        if extracted.columns:
            columns_lower = [str(col).lower() for col in extracted.columns]
            
            # If more than half the columns are documentation-related, it's probably docs
            doc_column_count = sum(1 for col in columns_lower 
                                 for indicator in doc_indicators 
                                 if indicator in col)
            
            if doc_column_count >= len(columns_lower) / 2:
                return False
        
        # Check if the data has numeric values (usually indicates real data)
        numeric_values = 0
        total_values = 0
        for row in extracted.rows[:10]:  # Check first 10 rows
            for value in row:
                total_values += 1
                try:
                    float(str(value))
                    numeric_values += 1
                except:
                    pass
        
        # If we have a good proportion of numeric values, it's likely data
        if total_values > 0 and numeric_values > total_values * 0.3:
            return True
        
        # Check data patterns
        if extracted.data_type in ['time_series', 'financial', 'statistical', 'csv', 'excel_sheet']:
            return True
        
        # Check if rows contain actual data values (not just descriptions)
        if extracted.rows:
            # Look for patterns that indicate real data
            first_row = extracted.rows[0]
            if any(isinstance(val, (int, float)) for val in first_row):
                return True
            
            # Check for date-like values
            for val in first_row:
                try:
                    pd.to_datetime(str(val))
                    return True
                except:
                    pass
        
        return False
    
    def _find_potential_data_links(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Find links that might lead to actual data"""
        
        soup = BeautifulSoup(html, 'html.parser')
        potential_links = []
        
        # Data-related keywords
        data_keywords = [
            'download', 'export', 'csv', 'json', 'excel', 'data', 'dataset',
            'file', 'raw', 'bulk', 'api', 'feed', 'stream', 'report', 'xlsx',
            'get', 'fetch', 'retrieve', 'access'
        ]
        
        # Check all links
        for element in soup.find_all(['a', 'button']):
            href = element.get('href', '')
            text = element.get_text().strip().lower()
            onclick = element.get('onclick', '').lower()
            title = element.get('title', '').lower()
            
            # Check if link text, href, or attributes contain data keywords
            combined_text = f"{text} {href.lower()} {onclick} {title}"
            if any(keyword in combined_text for keyword in data_keywords):
                
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    full_url = urljoin(base_url, href)
                    potential_links.append({
                        'url': full_url,
                        'text': element.get_text().strip()
                    })
        
        # Look for data-url attributes
        for element in soup.find_all(attrs={'data-url': True}):
            data_url = element.get('data-url')
            if data_url:
                potential_links.append({
                    'url': urljoin(base_url, data_url),
                    'text': element.get_text().strip() or 'Data Link'
                })
        
        # Look for forms that might submit to data endpoints
        for form in soup.find_all('form'):
            action = form.get('action', '')
            if action and any(keyword in action.lower() for keyword in ['data', 'download', 'export']):
                potential_links.append({
                    'url': urljoin(base_url, action),
                    'text': 'Form submission endpoint'
                })
        
        # Look for iframe sources that might be data
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and any(keyword in src.lower() for keyword in ['data', 'chart', 'table', 'dashboard']):
                potential_links.append({
                    'url': urljoin(base_url, src),
                    'text': 'Embedded Data Frame'
                })
        
        # Remove duplicates and return
        seen = set()
        unique_links = []
        for link in potential_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links[:10]  # Limit to 10 links
    
    def _llm_extract_any_data(self, html: str, url: str, context: str) -> Optional[ExtractedData]:
        """Use LLM to extract any data present in the HTML"""
        
        # Clean HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        
        prompt = f"""
Extract any structured data from this webpage based on the user's request.

User's Request: {context}

Webpage Content:
{text}

Instructions:
1. Look for ANY data values, not just documentation
2. Common patterns: tables, lists, statistics, measurements, prices, dates, etc.
3. If you find parameter documentation instead of data, look for example values or sample data
4. Create appropriate column names based on the data you find

Output ONLY valid JSON with:
{{
    "columns": ["col1", "col2", ...],
    "rows": [[val1, val2, ...], ...],
    "data_type": "what kind of data this is"
}}

If no actual data is found, return:
{{
    "columns": [],
    "rows": [],
    "data_type": "no_data_found"
}}
"""
        
        try:
            response = self.llm.chat([Message(role="system", content=prompt)])
            
            # Clean response
            if response.strip().startswith("```json"):
                response = response.strip()[7:-3]
            elif response.strip().startswith("```"):
                response = response.strip()[3:-3]
                
            data = json.loads(response)
            
            if data.get('rows') and data.get('data_type') != 'no_data_found':
                return ExtractedData(
                    source_url=url,
                    data_type=data.get('data_type', 'extracted'),
                    columns=data['columns'],
                    rows=data['rows'],
                    metadata={'extraction_context': context[:200]},
                    extraction_method="llm_intelligent_extraction",
                    confidence_score=0.7
                )
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
        
        return None
    
    def _format_results(self, extracted_data: List[ExtractedData], 
                       strategies: List[str]) -> str:
        """Format results with strategy information"""
        
        # Separate actual data from documentation
        actual_data = [d for d in extracted_data if self._contains_actual_data(d)]
        documentation = [d for d in extracted_data if not self._contains_actual_data(d)]
        
        result = {
            "status": "success" if actual_data else "partial",
            "data_found": len(actual_data) > 0,
            "extracted_data": [],
            "documentation_found": [],
            "extraction_strategies": strategies,
            "summary": ""
        }
        
        # Format actual data
        for data in actual_data:
            data_dict = data.model_dump()
            
            # Add data quality indicators
            if data.rows:
                data_dict['row_count'] = len(data.rows)
                data_dict['column_count'] = len(data.columns)
                
                # For time series data, add range info
                if any('year' in col.lower() or 'date' in col.lower() for col in data.columns):
                    data_dict['metadata']['data_range'] = self._get_date_range(data)
            
            result['extracted_data'].append(data_dict)
        
        # Format documentation (if no actual data found)
        if not actual_data and documentation:
            for doc in documentation:
                doc_dict = doc.model_dump()
                doc_dict['row_count'] = len(doc.rows)
                doc_dict['column_count'] = len(doc.columns)
                result['documentation_found'].append(doc_dict)
        
        # Generate summary
        result['summary'] = self._generate_summary(actual_data, documentation, strategies)
        
        # Add suggestions if only documentation was found
        if not actual_data and documentation:
            result['suggestions'] = [
                "Try searching for direct download links (CSV, JSON, Excel)",
                "Look for 'export' or 'download' buttons on the webpage",
                "Search for API documentation with example endpoints",
                "Try adding 'filetype:csv' or 'filetype:json' to your search"
            ]
        
        return json.dumps(result, indent=2)
    
    def _generate_summary(self, data: List[ExtractedData], 
                         docs: List[ExtractedData], 
                         strategies: List[str]) -> str:
        """Generate a helpful summary of what was found"""
        
        successful_strategies = [s for s in strategies if 'SUCCESS' in s]
        
        if data:
            total_rows = sum(len(d.rows) for d in data)
            data_types = list(set(d.data_type for d in data))
            return (f"Successfully extracted {len(data)} datasets with {total_rows} total rows. "
                   f"Data types: {', '.join(data_types)}. "
                   f"Successful strategy: {successful_strategies[-1] if successful_strategies else 'Direct extraction'}")
        elif docs:
            return (f"Found API documentation or parameter tables but no actual data values. "
                   f"The source may require specific API parameters or authentication. "
                   f"Tried {len(strategies)} strategies including: {', '.join(strategies[:3])}")
        else:
            return f"No data or documentation found at the provided URL. Strategies attempted: {len(strategies)}"
    
    def _get_date_range(self, data: ExtractedData) -> Dict[str, Any]:
        """Extract date range from data"""
        # Find date/year column
        date_col_idx = None
        for i, col in enumerate(data.columns):
            if 'year' in col.lower() or 'date' in col.lower():
                date_col_idx = i
                break
        
        if date_col_idx is not None and data.rows:
            dates = [row[date_col_idx] for row in data.rows if row[date_col_idx]]
            if dates:
                return {
                    'start': min(dates),
                    'end': max(dates),
                    'count': len(dates)
                }
        
        return {}
    
#TODO:: this could be a common method as a lot of LLM outputs have these fences 
def _strip_code_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        # drop the first line (``` or ```json)
        parts = s.split("\n", 1)
        s = parts[1] if len(parts) > 1 else ""
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()