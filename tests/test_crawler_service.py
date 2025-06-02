import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.services.crawler_service import CrawlerService, crawler_service
from app.models.models import (
    CrawlRequest,
    CrawlBatchRequest,
    DeepCrawlRequest,
    CrawlResult,
    CssExtractionSchema,
    ExtractionSchemaField
)


class TestCrawlerService:
    """CrawlerService单元测试"""

    @pytest.mark.unit
    async def test_singleton_pattern(self):
        """测试单例模式"""
        service1 = CrawlerService()
        service2 = CrawlerService()
        assert service1 is service2
        assert service1 is crawler_service

    @pytest.mark.unit
    async def test_crawl_url_success(
        self,
        sample_crawl_request,
        mock_async_web_crawler,
        mock_crawler_result
    ):
        """测试成功爬取单个URL"""
        # Act
        result = await crawler_service.crawl_url(sample_crawl_request)

        # Assert
        assert result.success is True
        assert result.url == sample_crawl_request.url
        assert result.status_code == 200
        assert result.markdown is not None
        assert result.error_message is None

        # 验证爬虫被正确调用
        mock_async_web_crawler.assert_called_once()

    @pytest.mark.unit
    async def test_crawl_url_with_css_selector(
        self,
        mock_async_web_crawler
    ):
        """测试使用CSS选择器爬取"""
        # Arrange
        request = CrawlRequest(
            url="https://www.anthropic.com/engineering/building-effective-agents",
            css_selector="article h1"
        )

        # Act
        result = await crawler_service.crawl_url(request)

        # Assert
        assert result.success is True
        # 验证CSS选择器被传递给配置
        call_args = mock_async_web_crawler.return_value.arun.call_args
        assert call_args[1]['config'].css_selector == "article h1"

    @pytest.mark.unit
    async def test_crawl_url_with_css_extraction_schema(
        self,
        mock_async_web_crawler
    ):
        """测试使用CSS提取模式"""
        # Arrange
        schema = CssExtractionSchema(
            name="TestSchema",
            baseSelector="body",
            fields=[
                ExtractionSchemaField(
                    name="title",
                    selector="h1",
                    type="text"
                )
            ]
        )
        request = CrawlRequest(
            url="https://www.anthropic.com/engineering/building-effective-agents",
            css_extraction_schema=schema
        )

        # Act
        result = await crawler_service.crawl_url(request)

        # Assert
        assert result.success is True
        # 验证提取策略被设置
        call_args = mock_async_web_crawler.return_value.arun.call_args
        assert call_args[1]['config'].extraction_strategy is not None

    @pytest.mark.unit
    async def test_crawl_url_timeout(self, sample_crawl_request):
        """测试爬取超时处理"""
        # Arrange
        with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.__aexit__.return_value = None
            mock_crawler.arun.side_effect = asyncio.TimeoutError()
            mock_class.return_value = mock_crawler

            # Act
            result = await crawler_service.crawl_url(sample_crawl_request)

            # Assert
            assert result.success is False
            assert "超时" in result.error_message

    @pytest.mark.unit
    async def test_crawl_url_exception(self, sample_crawl_request):
        """测试爬取异常处理"""
        # Arrange
        with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.__aexit__.return_value = None
            mock_crawler.arun.side_effect = Exception("Network error")
            mock_class.return_value = mock_crawler

            # Act
            result = await crawler_service.crawl_url(sample_crawl_request)

            # Assert
            assert result.success is False
            assert "Network error" in result.error_message

    @pytest.mark.unit
    async def test_crawl_multiple_urls_success(
        self,
        test_urls,
        mock_async_web_crawler,
        mock_crawler_result
    ):
        """测试批量爬取成功"""
        # Arrange
        request = CrawlBatchRequest(urls=test_urls)

        # Act
        results = await crawler_service.crawl_multiple_urls(request)

        # Assert
        assert len(results) == len(test_urls)
        for i, result in enumerate(results):
            assert result.success is True
            assert result.url == test_urls[i]

    @pytest.mark.unit
    async def test_crawl_multiple_urls_partial_failure(self, test_urls):
        """测试批量爬取部分失败"""
        # Arrange
        request = CrawlBatchRequest(urls=test_urls)

        with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.__aexit__.return_value = None

            # 第二个URL失败
            side_effects = []
            for i, url in enumerate(test_urls):
                if i == 1:
                    side_effects.append(Exception("Failed"))
                else:
                    result = MagicMock()
                    result.success = True
                    result.status_code = 200
                    result.markdown = f"Content for {url}"
                    side_effects.append(result)

            mock_crawler.arun.side_effect = side_effects
            mock_class.return_value = mock_crawler

            # Act
            results = await crawler_service.crawl_multiple_urls(request)

            # Assert
            assert len(results) == len(test_urls)
            assert results[0].success is True
            assert results[1].success is False
            assert results[2].success is True

    @pytest.mark.unit
    async def test_concurrent_crawling_limit(self, mock_settings):
        """测试并发爬取限制"""
        # Arrange
        mock_settings(MAX_CONCURRENT_CRAWLS=2)
        urls = [f"https://example{i}.com" for i in range(5)]
        request = CrawlBatchRequest(urls=urls)

        concurrent_count = 0
        max_concurrent = 0

        async def mock_arun(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.1)  # 模拟爬取时间
            concurrent_count -= 1

            result = MagicMock()
            result.success = True
            result.status_code = 200
            return result

        with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.__aexit__.return_value = None
            mock_crawler.arun.side_effect = mock_arun
            mock_class.return_value = mock_crawler

            # Act
            await crawler_service.crawl_multiple_urls(request)

            # Assert
            assert max_concurrent <= 2

    @pytest.mark.unit
    async def test_deep_crawl_success(self, mock_async_web_crawler):
        """测试深度爬取成功"""
        # Arrange
        request = DeepCrawlRequest(
            start_url="https://www.anthropic.com/engineering/building-effective-agents",
            max_depth=2,
            max_pages=10
        )

        # Mock深度爬取结果
        mock_results = []
        for i in range(3):
            result = MagicMock()
            result.url = f"https://www.anthropic.com/engineering/building-effective-agents/page{i}"
            result.success = True
            result.status_code = 200
            result.markdown = f"Page {i} content"
            mock_results.append(result)

        mock_async_web_crawler.return_value.arun.return_value = mock_results

        # Act
        results = await crawler_service.deep_crawl(request)

        # Assert
        assert len(results) == 3
        for result in results:
            assert result.success is True

    @pytest.mark.unit
    async def test_deep_crawl_with_patterns(self, mock_async_web_crawler):
        """测试带模式的深度爬取"""
        # Arrange
        request = DeepCrawlRequest(
            start_url="https://www.anthropic.com/engineering/building-effective-agents",
            max_depth=2,
            max_pages=5,
            include_patterns=["*/blog/*"],
            exclude_patterns=["*/admin/*", "*/login/*"]
        )

        # Act
        await crawler_service.deep_crawl(request)

        # Assert
        call_args = mock_async_web_crawler.return_value.arun.call_args
        config = call_args[1]['config']
        assert config.deep_crawl_strategy is not None

    @pytest.mark.unit
    async def test_crawler_pool_management(self):
        """测试爬虫池管理"""
        # 清空池
        CrawlerService._crawler_pool.clear()

        # 创建多个爬虫
        crawlers = []
        for _ in range(3):
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.__aexit__.return_value = None
            crawlers.append(mock_crawler)

        with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
            mock_class.side_effect = crawlers

            # 使用爬虫
            browser_config = crawler_service._create_browser_config()

            async with crawler_service.get_crawler(browser_config) as c1:
                pass
            async with crawler_service.get_crawler(browser_config) as c2:
                pass

            # 验证爬虫被重用
            assert len(CrawlerService._crawler_pool) == 2

    @pytest.mark.unit
    async def test_cleanup(self):
        """测试资源清理"""
        # Arrange
        mock_crawler = AsyncMock()
        CrawlerService._crawler_pool = [mock_crawler]

        # Act
        await CrawlerService.cleanup()

        # Assert
        assert len(CrawlerService._crawler_pool) == 0
        mock_crawler.__aexit__.assert_called_once()
