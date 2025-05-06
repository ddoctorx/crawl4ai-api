import asyncio
import json
from typing import Dict, Any, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from app.models.models import CrawlRequest, CrawlResult, LLMExtractionModel


class ExtractionService:
    """提取服务类，主要负责LLM提取"""

    @staticmethod
    async def extract_with_llm(request: CrawlRequest) -> CrawlResult:
        """使用LLM进行提取"""
        if not request.llm_extraction:
            return CrawlResult(
                url=request.url,
                success=False,
                error_message="LLM提取配置缺失"
            )

        try:
            # 配置浏览器
            browser_config = BrowserConfig(
                headless=True,
                java_script_enabled=request.js_enabled,
                viewport={"width": 1280, "height": 800}
            )

            # 配置LLM
            llm_config = LLMConfig(
                provider=request.llm_extraction.llm_config.provider,
                api_token=request.llm_extraction.llm_config.api_token
            )

            # 创建LLM提取策略
            llm_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                schema=request.llm_extraction.schema_data,
                instruction=request.llm_extraction.instruction,
                extraction_type="schema"
            )

            # 配置爬取参数
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS if request.bypass_cache else CacheMode.ENABLED,
                check_robots_txt=request.check_robots_txt,
                word_count_threshold=request.word_count_threshold,
                extraction_strategy=llm_strategy,
                page_timeout=80000  # 增加超时时间，LLM处理可能较慢
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=request.url, config=crawler_config)

                return CrawlResult(
                    url=request.url,
                    success=result.success,
                    status_code=result.status_code,
                    markdown=result.markdown if result.success else None,
                    extracted_content=result.extracted_content if result.success and result.extracted_content else None,
                    error_message=result.error_message if not result.success else None,
                    media=result.media if result.success else None,
                    links=result.links if result.success else None
                )
        except Exception as e:
            return CrawlResult(
                url=request.url,
                success=False,
                error_message=f"LLM提取失败: {str(e)}"
            )
