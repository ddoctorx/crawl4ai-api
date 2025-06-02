from app.models.models import CrawlResult, CrawlRequest
from app.config import settings
from app.main import app
import os
import sys
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

# 添加项目路径
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


# 配置测试环境
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境变量"""
    os.environ["TESTING"] = "true"
    os.environ["API_KEY_ENABLED"] = "false"
    os.environ["RATE_LIMIT_ENABLED"] = "false"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["BROWSER_HEADLESS"] = "true"
    yield
    os.environ.pop("TESTING", None)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock配置设置"""
    def _mock_settings(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setattr(settings, key, value)
    return _mock_settings


# Mock fixtures
@pytest.fixture
def mock_crawler():
    """Mock爬虫实例"""
    crawler = AsyncMock()
    crawler.__aenter__ = AsyncMock(return_value=crawler)
    crawler.__aexit__ = AsyncMock(return_value=None)
    return crawler


@pytest.fixture
def mock_crawler_result():
    """Mock爬虫结果"""
    result = MagicMock()
    result.success = True
    result.status_code = 200
    result.markdown = "# Test Page\n\nThis is test content."
    result.error_message = None
    result.media = {"images": []}
    result.links = {"internal": [], "external": []}
    result.extracted_content = None
    return result


@pytest.fixture
def sample_crawl_request():
    """示例爬取请求"""
    return CrawlRequest(
        url="https://www.anthropic.com/engineering/building-effective-agents",
        bypass_cache=True,
        js_enabled=True,
        word_count_threshold=10
    )


@pytest.fixture
def sample_crawl_result():
    """示例爬取结果"""
    return CrawlResult(
        url="https://www.anthropic.com/engineering/building-effective-agents",
        success=True,
        status_code=200,
        markdown="# Example Page\n\nContent here.",
        error_message=None
    )


@pytest.fixture
def mock_async_web_crawler(mock_crawler, mock_crawler_result):
    """Mock AsyncWebCrawler类"""
    with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
        mock_class.return_value = mock_crawler
        mock_crawler.arun.return_value = mock_crawler_result
        yield mock_class


# 测试数据
@pytest.fixture
def test_urls():
    """测试URL列表"""
    return [
        "https://www.anthropic.com/engineering/building-effective-agents",
        "https://test.com",
        "https://sample.org"
    ]


@pytest.fixture
def invalid_urls():
    """无效URL列表"""
    return [
        "not-a-url",
        "ftp://invalid.com",
        "javascript:alert(1)",
        ""
    ]


# API Key fixtures
@pytest.fixture
def api_key_headers():
    """API密钥请求头"""
    return {"Authorization": "Bearer test-api-key-123"}


@pytest.fixture
def enable_api_auth(mock_settings):
    """启用API认证"""
    mock_settings(
        API_KEY_ENABLED=True,
        API_KEYS=["test-api-key-123", "test-api-key-456"]
    )


# Rate limiting fixtures
@pytest.fixture
def enable_rate_limit(mock_settings):
    """启用速率限制"""
    mock_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_CALLS=5,
        RATE_LIMIT_PERIOD=60
    )
