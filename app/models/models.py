from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl


class BrowserConfigModel(BaseModel):
    """浏览器配置模型"""
    headless: bool = True
    java_script_enabled: bool = True
    viewport_width: Optional[int] = 1280
    viewport_height: Optional[int] = 800
    verbose: bool = False


class ExtractionSchemaField(BaseModel):
    """CSS提取策略字段"""
    name: str
    selector: str
    type: str = "text"
    attribute: Optional[str] = None


class CssExtractionSchema(BaseModel):
    """CSS提取策略模式"""
    name: str
    baseSelector: str
    fields: List[ExtractionSchemaField]


class LLMConfigModel(BaseModel):
    """LLM配置模型"""
    provider: str
    api_token: Optional[str] = None


class LLMExtractionModel(BaseModel):
    """LLM提取模型"""
    schema_data: Dict[str, Any]
    instruction: str
    llm_config: LLMConfigModel


class CrawlRequest(BaseModel):
    """爬取请求模型"""
    url: str
    bypass_cache: bool = False
    check_robots_txt: bool = True
    word_count_threshold: int = 20
    js_enabled: bool = True
    css_selector: Optional[str] = None
    css_extraction_schema: Optional[CssExtractionSchema] = None
    llm_extraction: Optional[LLMExtractionModel] = None


class CrawlBatchRequest(BaseModel):
    """批量爬取请求"""
    urls: List[str]
    bypass_cache: bool = False
    check_robots_txt: bool = True
    word_count_threshold: int = 20
    js_enabled: bool = True
    stream: bool = False


class DeepCrawlRequest(BaseModel):
    """深度爬取请求"""
    start_url: str
    max_depth: int = 1
    max_pages: int = 10
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    bypass_cache: bool = False
    stream: bool = False


class CrawlResult(BaseModel):
    """爬取结果模型"""
    url: str
    success: bool
    status_code: Optional[int] = None
    markdown: Optional[str] = None
    extracted_content: Optional[str] = None
    error_message: Optional[str] = None
    media: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None


class CrawlResponse(BaseModel):
    """爬取响应模型"""
    results: List[CrawlResult]
