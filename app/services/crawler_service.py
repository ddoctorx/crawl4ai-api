import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from app.models.models import (
    CrawlRequest,
    CrawlBatchRequest,
    DeepCrawlRequest,
    CrawlResult,
)
from app.config import settings
from app.utils.exceptions import CrawlerError, InvalidURLError

logger = logging.getLogger(__name__)


class CrawlerService:
    """
    爬虫服务类

    提供网页爬取的核心功能，包括单页面爬取、批量爬取和深度爬取。
    """

    _instance: Optional['CrawlerService'] = None
    _crawler_pool: List[AsyncWebCrawler] = []
    _pool_size: int = 5

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    @asynccontextmanager
    async def get_crawler(cls, browser_config: BrowserConfig):
        """
        从爬虫池获取或创建爬虫实例

        Args:
            browser_config: 浏览器配置

        Yields:
            AsyncWebCrawler: 爬虫实例
        """
        crawler = None
        try:
            # 尝试从池中获取
            if cls._crawler_pool:
                crawler = cls._crawler_pool.pop()
            else:
                crawler = AsyncWebCrawler(config=browser_config)
                await crawler.__aenter__()

            yield crawler

        finally:
            # 归还到池中
            if crawler and len(cls._crawler_pool) < cls._pool_size:
                cls._crawler_pool.append(crawler)
            elif crawler:
                await crawler.__aexit__(None, None, None)

    @staticmethod
    def _create_browser_config(js_enabled: bool = True) -> BrowserConfig:
        """创建统一的浏览器配置"""
        return BrowserConfig(
            headless=settings.BROWSER_HEADLESS,
            java_script_enabled=js_enabled,
            viewport={
                "width": settings.VIEWPORT_WIDTH,
                "height": settings.VIEWPORT_HEIGHT
            },
            verbose=settings.DEBUG,
            extra_args=settings.BROWSER_EXTRA_ARGS
        )

    @staticmethod
    def _create_crawler_config(
        request: Union[CrawlRequest, CrawlBatchRequest, DeepCrawlRequest],
        extraction_strategy=None,
        deep_crawl_strategy=None
    ) -> CrawlerRunConfig:
        """创建统一的爬虫配置"""
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if request.bypass_cache else CacheMode.ENABLED,
            check_robots_txt=request.check_robots_txt,
            word_count_threshold=request.word_count_threshold,
            page_timeout=settings.PAGE_TIMEOUT,
            wait_for_images=settings.WAIT_FOR_IMAGES,
        )

        if extraction_strategy:
            config.extraction_strategy = extraction_strategy

        if deep_crawl_strategy:
            config.deep_crawl_strategy = deep_crawl_strategy

        if hasattr(request, 'css_selector') and request.css_selector:
            config.css_selector = request.css_selector

        return config

    async def crawl_url(self, request: CrawlRequest) -> CrawlResult:
        """
        爬取单个URL

        Args:
            request: 爬取请求对象

        Returns:
            CrawlResult: 爬取结果

        Raises:
            CrawlerError: 爬取过程中的错误
        """
        logger.info(f"开始爬取URL: {request.url}")

        try:
            browser_config = self._create_browser_config(request.js_enabled)
            crawler_config = self._create_crawler_config(request)

            # 处理CSS提取模式
            if request.css_extraction_schema:
                schema = {
                    "name": request.css_extraction_schema.name,
                    "baseSelector": request.css_extraction_schema.baseSelector,
                    "fields": [field.dict() for field in request.css_extraction_schema.fields]
                }
                crawler_config.extraction_strategy = JsonCssExtractionStrategy(
                    schema)

            async with self.get_crawler(browser_config) as crawler:
                result = await crawler.arun(url=request.url, config=crawler_config)

                return self._parse_crawl_result(request.url, result)

        except asyncio.TimeoutError:
            logger.error(f"爬取超时: {request.url}")
            return CrawlResult(
                url=request.url,
                success=False,
                error_message="爬取超时"
            )
        except Exception as e:
            logger.error(f"爬取失败 {request.url}: {str(e)}", exc_info=True)
            return CrawlResult(
                url=request.url,
                success=False,
                error_message=f"爬取失败: {str(e)}"
            )

    async def crawl_multiple_urls(self, request: CrawlBatchRequest) -> List[CrawlResult]:
        """
        批量爬取URL

        使用并发控制避免资源耗尽
        """
        logger.info(f"开始批量爬取 {len(request.urls)} 个URL")

        browser_config = self._create_browser_config(request.js_enabled)
        crawler_config = self._create_crawler_config(request)

        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CRAWLS)

        async def crawl_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                try:
                    async with self.get_crawler(browser_config) as crawler:
                        result = await crawler.arun(url=url, config=crawler_config)
                        return self._parse_crawl_result(url, result)
                except Exception as e:
                    logger.error(f"批量爬取失败 {url}: {str(e)}")
                    return CrawlResult(
                        url=url,
                        success=False,
                        error_message=str(e)
                    )

        # 并发执行所有爬取任务
        tasks = [crawl_with_semaphore(url) for url in request.urls]
        results = await asyncio.gather(*tasks)

        return results

    async def deep_crawl(self, request: DeepCrawlRequest) -> List[CrawlResult]:
        """
        深度爬取网站

        Args:
            request: 深度爬取请求

        Returns:
            List[CrawlResult]: 爬取结果列表
        """
        logger.info(f"开始深度爬取: {request.start_url}, 深度: {request.max_depth}")

        browser_config = self._create_browser_config(True)

        # 配置深度爬取策略
        deep_crawl_strategy = BFSDeepCrawlStrategy(
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            include_patterns=request.include_patterns or [],
            exclude_patterns=request.exclude_patterns or []
        )

        crawler_config = self._create_crawler_config(
            request,
            deep_crawl_strategy=deep_crawl_strategy
        )

        try:
            async with self.get_crawler(browser_config) as crawler:
                results = await crawler.arun(
                    url=request.start_url,
                    config=crawler_config
                )

                # 处理深度爬取结果
                if isinstance(results, list):
                    return [self._parse_crawl_result(r.url, r) for r in results]
                else:
                    # 兼容单个结果的情况
                    return [self._parse_crawl_result(results.url, results)]

        except Exception as e:
            logger.error(f"深度爬取失败: {str(e)}", exc_info=True)
            return [CrawlResult(
                url=request.start_url,
                success=False,
                error_message=f"深度爬取失败: {str(e)}"
            )]

    @staticmethod
    def _parse_crawl_result(url: str, result: Any) -> CrawlResult:
        """解析爬取结果为统一格式"""
        return CrawlResult(
            url=url,
            success=result.success,
            status_code=getattr(result, 'status_code', None),
            markdown=result.markdown if result.success else None,
            extracted_content=result.extracted_content if result.success and hasattr(
                result, 'extracted_content') else None,
            error_message=getattr(result, 'error_message',
                                  None) if not result.success else None,
            media=result.media if result.success and hasattr(
                result, 'media') else None,
            links=result.links if result.success and hasattr(
                result, 'links') else None
        )

    @classmethod
    async def cleanup(cls):
        """清理爬虫池资源"""
        for crawler in cls._crawler_pool:
            await crawler.__aexit__(None, None, None)
        cls._crawler_pool.clear()


# 创建服务实例
crawler_service = CrawlerService()
