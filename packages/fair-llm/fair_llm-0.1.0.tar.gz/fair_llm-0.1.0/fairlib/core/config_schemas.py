# core/config_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

"""
This module defines the canonical Pydantic schemas for the application's configuration.
By using these models, we ensure that the settings loaded from `settings.yml` are
always validated, type-safe, and have a predictable structure. This prevents
runtime errors caused by missing or malformed configuration and provides a clear,
documented reference for all available settings.
"""


class APIKeys(BaseModel):
    """
    Schema for storing API keys for various third-party services.
    Fields are marked as Optional, allowing the application to function even
    if some keys are not provided (e.g., if only using local models).
    """
    openai_api_key: Optional[str] = None
    """The API key for OpenAI services (e.g., 'sk-...')"""
    
    anthropic_api_key: Optional[str] = None
    """The API key for Anthropic services."""


class SearchEngineSettings(BaseModel):
    """
    Schema for storing search engine related data.
    """
    google_cse_search_api: Optional[str] = None
    """The API key for Google CSE Web searches."""
    
    google_cse_search_engine_id: Optional[str] = None
    """ID of Google CSE search engine."""
    
    web_search_cache_ttl: Optional[int] = 3600
    web_search_cache_max_size: Optional[int] = 1000
    web_search_max_results: Optional[int] = 10


class ModelSettings(BaseModel):
    """
    Schema for defining the settings of a single language model.
    This allows the application to configure multiple models and refer to them
    by a key in the main settings file.
    """
    provider: str
    """The name of the provider, e.g., 'openai', 'anthropic', 'ollama'."""
    
    model_name: str
    """The specific name of the model, e.g., 'gpt-4-turbo', 'claude-3-opus-20240229'."""
    
    temperature: float = 0.7
    """The sampling temperature for the model's output (0.0 to 2.0). Defaults to 0.7."""
    
    max_tokens: Optional[int] = 2000
    """Maximum number of tokens to generate. Defaults to 2000."""


class SecuritySettings(BaseModel):
    """
    Schema for configuring the framework's security features.
    """
    enable_input_validation: bool = True
    """If True, the input validator will scan user prompts for malicious patterns."""
    
    max_input_length: int = 10000
    """Maximum allowed length for user inputs."""


# ===============================
# RAG System Configuration Classes
# ===============================

class RAGPathSettings(BaseModel):
    """Schema for RAG system paths."""
    files_directory: str = "/app/docs"
    """Directory for storing uploaded documents"""
    
    vector_store_dir: str = "/app/vector_store"
    """Directory for vector store files (e.g., FAISS)"""


class DocumentProcessingSettings(BaseModel):
    """Schema for document processing configuration."""
    supported_extensions: List[str] = Field(
        default_factory=lambda: [".pdf", ".docx", ".txt", ".csv", ".xlsx", ".sql", ".pptx"]
    )
    """List of supported file extensions for processing"""
    
    max_chunk_chars: int = Field(default=1500, ge=100)
    """Maximum characters per chunk when splitting documents"""
    
    enable_ocr: bool = True
    """Enable OCR for image-based PDFs and images in documents"""
    
    ocr_dpi: int = Field(default=200, ge=72, le=600)
    """DPI setting for OCR processing"""


class EmbeddingSettings(BaseModel):
    """Schema for embedding model configuration."""
    embedding_model: str = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    """Model for generating document embeddings"""
    
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    """Model for re-ranking retrieved documents"""
    
    batch_size: int = Field(default=64, ge=1)
    """Batch size for embedding generation"""


class RetrievalSettings(BaseModel):
    """Schema for retrieval configuration."""
    default_top_k: int = Field(default=15, ge=1)
    """Default number of documents to retrieve"""
    
    pool_multiplier: int = Field(default=3, ge=1)
    """Multiplier for initial retrieval pool size"""
    
    max_initial_retrieval_docs: int = Field(default=75, ge=1)
    """Maximum documents in initial retrieval"""
    
    rerank_enabled: bool = True
    """Enable cross-encoder reranking"""


class VectorStoreSettings(BaseModel):
    """Schema for vector store configuration."""
    backend: str = Field(default="faiss", pattern="^(faiss|chroma|qdrant|pinecone)$")
    """Vector store backend to use"""
    
    use_gpu: bool = True
    """Attempt to use GPU acceleration if available"""
    
    index_type: str = "IVF"
    """FAISS index type (for FAISS backend)"""


class RAGSystemSettings(BaseModel):
    """
    Schema for the complete RAG (Retrieval-Augmented Generation) system.
    This is a generic configuration that can be used by any pipeline that needs RAG.
    """
    paths: RAGPathSettings = Field(default_factory=RAGPathSettings)
    """File and storage paths"""
    
    document_processing: DocumentProcessingSettings = Field(default_factory=DocumentProcessingSettings)
    """Document processing settings"""
    
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    """Embedding model configuration"""
    
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    """Retrieval parameters"""
    
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    """Vector store configuration"""


# ===============================
# Cache Configuration
# ===============================

class CacheSettings(BaseModel):
    """Schema for system-wide cache configuration."""
    query_cache_enabled: bool = True
    """Enable query result caching"""
    
    max_cache_size: int = Field(default=1000, ge=1)
    """Maximum number of cached items"""
    
    cache_ttl: int = Field(default=3600, ge=0)
    """Cache time-to-live in seconds (0 = no expiry)"""
    
    redis_url: Optional[str] = None
    """Redis URL for distributed caching (optional)"""


# ===============================
# LLM Configuration
# ===============================

class LLMSettings(BaseModel):
    """Schema for LLM-specific settings."""
    max_retries: int = Field(default=3, ge=0)
    """Maximum retry attempts for LLM calls"""
    
    timeout: int = Field(default=120, ge=10)
    """Timeout in seconds for LLM calls"""
    
    streaming_enabled: bool = True
    """Enable streaming responses where supported"""


# ===============================
# Main Application Settings
# ===============================

class AppSettings(BaseModel):
    """
    The main configuration schema for the entire FAIR-LLM application.
    This model aggregates all other configuration schemas and serves as the top-level
    object for application settings.
    """
    api_keys: APIKeys
    """A nested object containing all third-party API keys."""
    
    models: Dict[str, ModelSettings]
    """
    A dictionary mapping a custom alias (e.g., 'default_gpt', 'fast_claude')
    to its specific model settings.
    """
    
    default_model: str
    """
    The key (from the 'models' dictionary) of the model to be used by default
    across the application.
    """
    
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    """
    Security settings. `default_factory` ensures that if this
    section is missing from the YAML file, a default `SecuritySettings` object
    is created.
    """
    
    search_engine: SearchEngineSettings = Field(default_factory=SearchEngineSettings)
    """Search engine configuration with defaults."""
    
    rag_system: Optional[RAGSystemSettings] = Field(default_factory=RAGSystemSettings)
    """
    RAG system configuration. This is generic and can be used by any pipeline
    that needs document retrieval capabilities.
    """
    
    cache: CacheSettings = Field(default_factory=CacheSettings)
    """System-wide cache configuration."""
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    """LLM-specific settings."""