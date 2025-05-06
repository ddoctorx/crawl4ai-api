import asyncio
from typing import Dict, List, Optional, Any, Union
import json

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from app.models.models import (
    CrawlRequest,
    CrawlBatchRequest,
    DeepCrawlRequest,
    CrawlResult,
    BrowserConfigModel
)


class CrawlerService:
    """爬虫服务类"""

    @staticmethod
    async def crawl_url(request: CrawlRequest) -> CrawlResult:
        """爬取单个URL"""
        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True,
            java_script_enabled=request.js_enabled,
            viewport={"width": 1280, "height": 800},
            verbose=False
        )

        # 配置爬取参数
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if request.bypass_cache else CacheMode.ENABLED,
            check_robots_txt=request.check_robots_txt,
            word_count_threshold=request.word_count_threshold,
            css_selector=request.css_selector,
        )

        # 如果提供了CSS提取模式
        if request.css_extraction_schema:
            schema = {
                "name": request.css_extraction_schema.name,
                "baseSelector": request.css_extraction_schema.baseSelector,
                "fields": [field.dict() for field in request.css_extraction_schema.fields]
            }
            crawler_config.extraction_strategy = JsonCssExtractionStrategy(
                schema)

        # LLM 提取在 extraction_service.py 实现

        async with AsyncWebCrawler(config=browser_config) as crawler:
            try:
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
                    error_message=str(e)
                )

    @staticmethod
    async def crawl_multiple_urls(request: CrawlBatchRequest) -> List[CrawlResult]:
        """批量爬取URL"""
        results = []

        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True,
            java_script_enabled=request.js_enabled,
            viewport={"width": 1280, "height": 800}
        )

        # 配置爬取参数
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if request.bypass_cache else CacheMode.ENABLED,
            check_robots_txt=request.check_robots_txt,
            word_count_threshold=request.word_count_threshold,
            stream=request.stream
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            try:
                if request.stream:
                    # 流模式处理
                    async for result in await crawler.arun_many(
                        urls=request.urls,
                        config=crawler_config
                    ):
                        results.append(
                            CrawlResult(
                                url=result.url,
                                success=result.success,
                                status_code=result.status_code,
                                markdown=result.markdown if result.success else None,
                                error_message=result.error_message if not result.success else None,
                                media=result.media if result.success else None,
                                links=result.links if result.success else None
                            )
                        )
                else:
                    # 非流模式
                    results_container = await crawler.arun_many(
                        urls=request.urls,
                        config=crawler_config
                    )

                    for result in results_container:
                        results.append(
                            CrawlResult(
                                url=result.url,
                                success=result.success,
                                status_code=result.status_code,
                                markdown=result.markdown if result.success else None,
                                error_message=result.error_message if not result.success else None,
                                media=result.media if result.success else None,
                                links=result.links if result.success else None
                            )
                        )
            except Exception as e:
                # 如果出现异常，为每个URL创建一个错误结果
                for url in request.urls:
                    results.append(
                        CrawlResult(
                            url=url,
                            success=False,
                            error_message=str(e)
                        )
                    )

        return results

    @staticmethod
    async def deep_crawl(request: DeepCrawlRequest) -> List[CrawlResult]:
        """深度爬取URL"""
        results = []

        # 配置浏览器
        browser_config = BrowserConfig(
            headless=True,
            java_script_enabled=True,
            viewport={"width": 1280, "height": 800}
        )

        # 配置深度爬取策略
        deep_crawl_strategy = BFSDeepCrawlStrategy(
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns
        )

        # 配置爬取参数
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if request.bypass_cache else CacheMode.ENABLED,
            check_robots_txt=True,
            deep_crawl_strategy=deep_crawl_strategy,
            stream=request.stream
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            try:
                if request.stream:
                    # 流模式处理
                    async for result in await crawler.arun(
                        url=request.start_url,
                        config=crawler_config
                    ):
                        results.append(
                            CrawlResult(
                                url=result.url,
                                success=result.success,
                                status_code=result.status_code,
                                markdown=result.markdown if result.success else None,
                                error_message=result.error_message if not result.success else None,
                                media=result.media if result.success else None,
                                links=result.links if result.success else None
                            )
                        )
                else:
                    # 非流模式
                    results_container = await crawler.arun(
                        url=request.start_url,
                        config=crawler_config
                    )

                    # 深度爬取结果处理 - 在新版API中，深度爬取直接返回结果列表
                    if isinstance(results_container, list):
                        for result in results_container:
                            results.append(
                                CrawlResult(
                                    url=result.url,
                                    success=result.success,
                                    status_code=result.status_code,
                                    markdown=result.markdown if result.success else None,
                                    error_message=result.error_message if not result.success else None,
                                    media=result.media if result.success else None,
                                    links=result.links if result.success else None
                                )
                            )
                    # 兼容旧版API
                    elif hasattr(results_container, 'deep_crawl_results'):
                        for result in results_container.deep_crawl_results:
                            results.append(
                                CrawlResult(
                                    url=result.url,
                                    success=result.success,
                                    status_code=result.status_code,
                                    markdown=result.markdown if result.success else None,
                                    error_message=result.error_message if not result.success else None,
                                    media=result.media if result.success else None,
                                    links=result.links if result.success else None
                                )
                            )
            except Exception as e:
                results.append(
                    CrawlResult(
                        url=request.start_url,
                        success=False,
                        error_message=str(e)
                    )
                )

        return results
