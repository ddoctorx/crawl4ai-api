import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from app.models.models import CrawlResult


class TestCrawlAPI:
    """爬取API端点集成测试"""

    @pytest.mark.integration
    async def test_health_check(self, async_client: AsyncClient):
        """测试健康检查端点"""
        response = await async_client.get("/api/crawl/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "健康"
        assert data["service"] == "crawl4ai-api"

    @pytest.mark.integration
    async def test_crawl_single_url_success(
        self,
        async_client: AsyncClient,
        sample_crawl_result
    ):
        """测试成功爬取单个URL"""
        with patch("app.services.crawler_service.crawler_service.crawl_url") as mock_crawl:
            mock_crawl.return_value = sample_crawl_result

            response = await async_client.post(
                "/api/crawl/url",
                json={
                    "url": "https://www.anthropic.com/engineering/building-effective-agents",
                    "bypass_cache": True,
                    "js_enabled": True
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["url"] == "https://www.anthropic.com/engineering/building-effective-agents"
            assert data["markdown"] is not None

    @pytest.mark.integration
    async def test_crawl_single_url_invalid_url(self, async_client: AsyncClient):
        """测试无效URL"""
        response = await async_client.post(
            "/api/crawl/url",
            json={
                "url": "not-a-valid-url",
                "bypass_cache": True
            }
        )

        assert response.status_code == 400
        assert "无效的URL" in response.json()["detail"]

    @pytest.mark.integration
    async def test_crawl_single_url_with_css_selector(
        self,
        async_client: AsyncClient,
        sample_crawl_result
    ):
        """测试带CSS选择器的爬取"""
        with patch("app.services.crawler_service.crawler_service.crawl_url") as mock_crawl:
            mock_crawl.return_value = sample_crawl_result

            response = await async_client.post(
                "/api/crawl/url",
                json={
                    "url": "https://www.anthropic.com/engineering/building-effective-agents",
                    "css_selector": "article h1"
                }
            )

            assert response.status_code == 200
            # 验证CSS选择器被传递
            call_args = mock_crawl.call_args[0][0]
            assert call_args.css_selector == "article h1"

    @pytest.mark.integration
    async def test_crawl_single_url_with_extraction_schema(
        self,
        async_client: AsyncClient,
        sample_crawl_result
    ):
        """测试带提取模式的爬取"""
        with patch("app.services.crawler_service.crawler_service.crawl_url") as mock_crawl:
            mock_crawl.return_value = sample_crawl_result

            response = await async_client.post(
                "/api/crawl/url",
                json={
                    "url": "https://www.anthropic.com/engineering/building-effective-agents",
                    "css_extraction_schema": {
                        "name": "ArticleExtractor",
                        "baseSelector": "article",
                        "fields": [
                            {
                                "name": "title",
                                "selector": "h1",
                                "type": "text"
                            },
                            {
                                "name": "content",
                                "selector": "p",
                                "type": "text"
                            }
                        ]
                    }
                }
            )

            assert response.status_code == 200

    @pytest.mark.integration
    async def test_batch_crawl_success(
        self,
        async_client: AsyncClient,
        test_urls
    ):
        """测试批量爬取成功"""
        # Mock结果
        mock_results = [
            CrawlResult(
                url=url,
                success=True,
                status_code=200,
                markdown=f"Content for {url}"
            )
            for url in test_urls
        ]

        with patch("app.services.crawler_service.crawler_service.crawl_multiple_urls") as mock_crawl:
            mock_crawl.return_value = mock_results

            response = await async_client.post(
                "/api/crawl/batch",
                json={
                    "urls": test_urls,
                    "bypass_cache": True,
                    "js_enabled": True
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == len(test_urls)
            for result in data["results"]:
                assert result["success"] is True

    @pytest.mark.integration
    async def test_batch_crawl_invalid_urls(
        self,
        async_client: AsyncClient,
        invalid_urls
    ):
        """测试批量爬取包含无效URL"""
        response = await async_client.post(
            "/api/crawl/batch",
            json={
                "urls": invalid_urls,
                "bypass_cache": True
            }
        )

        assert response.status_code == 400
        assert "包含无效URL" in response.json()["detail"]

    @pytest.mark.integration
    async def test_deep_crawl_success(self, async_client: AsyncClient):
        """测试深度爬取成功"""
        mock_results = [
            CrawlResult(
                url=f"https://www.anthropic.com/engineering/building-effective-agents/page{i}",
                success=True,
                status_code=200,
                markdown=f"Page {i} content"
            )
            for i in range(3)
        ]

        with patch("app.services.crawler_service.crawler_service.deep_crawl") as mock_crawl:
            mock_crawl.return_value = mock_results

            response = await async_client.post(
                "/api/crawl/deep",
                json={
                    "start_url": "https://www.anthropic.com/engineering/building-effective-agents",
                    "max_depth": 2,
                    "max_pages": 10,
                    "include_patterns": ["*/blog/*"],
                    "exclude_patterns": ["*/admin/*"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 3

    @pytest.mark.integration
    async def test_api_with_auth_enabled(
        self,
        async_client: AsyncClient,
        enable_api_auth,
        api_key_headers
    ):
        """测试启用API认证"""
        response = await async_client.get(
            "/api/crawl/health",
            headers=api_key_headers
        )

        assert response.status_code == 200

    @pytest.mark.integration
    async def test_api_without_auth_when_required(
        self,
        async_client: AsyncClient,
        enable_api_auth
    ):
        """测试缺少认证时的响应"""
        response = await async_client.post(
            "/api/crawl/url",
            json={
                "url": "https://www.anthropic.com/engineering/building-effective-agents"}
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_rate_limiting(
        self,
        async_client: AsyncClient,
        enable_rate_limit
    ):
        """测试速率限制"""
        # 发送超过限制的请求
        for i in range(6):
            response = await async_client.get("/api/crawl/health")

            if i < 5:
                assert response.status_code == 200
                assert "X-RateLimit-Remaining" in response.headers
            else:
                # 第6个请求应该被限制
                assert response.status_code == 429
                assert "retry_after" in response.json()["detail"]

    @pytest.mark.integration
    async def test_error_handling(self, async_client: AsyncClient):
        """测试错误处理"""
        with patch("app.services.crawler_service.crawler_service.crawl_url") as mock_crawl:
            mock_crawl.side_effect = Exception("Unexpected error")

            response = await async_client.post(
                "/api/crawl/url",
                json={
                    "url": "https://www.anthropic.com/engineering/building-effective-agents"}
            )

            # 应该返回失败结果而不是500错误
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Unexpected error" in data["error_message"]
