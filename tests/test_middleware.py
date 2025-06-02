import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.middleware import (
    RateLimitMiddleware,
    APIKeyMiddleware,
    LoggingMiddleware,
    ErrorHandlerMiddleware
)
from app.config import settings


class TestRateLimitMiddleware:
    """速率限制中间件测试"""

    @pytest.fixture
    def rate_limit_app(self):
        """创建带速率限制的测试应用"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=3, period=60)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        return app

    @pytest.mark.unit
    def test_rate_limit_allows_requests_within_limit(self, rate_limit_app):
        """测试在限制内的请求"""
        client = TestClient(rate_limit_app)

        # 前3个请求应该成功
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200
            assert int(response.headers["X-RateLimit-Remaining"]) == 2 - i

    @pytest.mark.unit
    def test_rate_limit_blocks_excess_requests(self, rate_limit_app):
        """测试超过限制的请求"""
        client = TestClient(rate_limit_app)

        # 发送4个请求
        for i in range(4):
            response = client.get("/test")

            if i < 3:
                assert response.status_code == 200
            else:
                # 第4个请求应该被阻止
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.json()[
                    "detail"]["error"]

    @pytest.mark.unit
    def test_rate_limit_window_sliding(self, rate_limit_app):
        """测试滑动窗口机制"""
        client = TestClient(rate_limit_app)

        # 修改中间件实例以使用更短的时间窗口
        middleware = None
        for m in rate_limit_app.middleware:
            if hasattr(m, 'cls') and m.cls == RateLimitMiddleware:
                middleware = m
                m.kwargs['period'] = 1  # 1秒窗口
                break

        # 发送3个请求
        for _ in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # 第4个应该被阻止
        response = client.get("/test")
        assert response.status_code == 429

        # 等待窗口过期
        time.sleep(1.1)

        # 现在应该可以再次请求
        response = client.get("/test")
        assert response.status_code == 200


class TestAPIKeyMiddleware:
    """API密钥中间件测试"""

    @pytest.fixture
    def api_key_app(self, mock_settings):
        """创建带API密钥认证的测试应用"""
        mock_settings(
            API_KEY_ENABLED=True,
            API_KEYS=["valid-key-123", "valid-key-456"]
        )

        app = FastAPI()
        app.add_middleware(APIKeyMiddleware)

        @app.get("/")
        async def root():
            return {"message": "public"}

        @app.get("/protected")
        async def protected():
            return {"message": "protected"}

        return app

    @pytest.mark.unit
    def test_api_key_allows_public_endpoints(self, api_key_app):
        """测试公开端点不需要认证"""
        client = TestClient(api_key_app)

        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_api_key_blocks_without_auth(self, api_key_app):
        """测试无认证访问受保护端点"""
        client = TestClient(api_key_app)

        response = client.get("/protected")
        assert response.status_code == 401
        assert "Missing or invalid authorization header" in response.json()[
            "detail"]

    @pytest.mark.unit
    def test_api_key_allows_with_valid_key(self, api_key_app):
        """测试有效密钥访问"""
        client = TestClient(api_key_app)

        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer valid-key-123"}
        )
        assert response.status_code == 200

    @pytest.mark.unit
    def test_api_key_blocks_invalid_key(self, api_key_app):
        """测试无效密钥"""
        client = TestClient(api_key_app)

        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]


class TestLoggingMiddleware:
    """日志中间件测试"""

    @pytest.fixture
    def logging_app(self):
        """创建带日志中间件的测试应用"""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        return app

    @pytest.mark.unit
    def test_logging_successful_request(self, logging_app, caplog):
        """测试成功请求的日志记录"""
        client = TestClient(logging_app)

        with caplog.at_level("INFO"):
            response = client.get("/test")

            assert response.status_code == 200
            assert "Request: GET /test" in caplog.text
            assert "Response: GET /test - Status: 200" in caplog.text
            assert "X-Response-Time" in response.headers

    @pytest.mark.unit
    def test_logging_error_request(self, logging_app, caplog):
        """测试错误请求的日志记录"""
        client = TestClient(logging_app)

        with caplog.at_level("ERROR"):
            with pytest.raises(ValueError):
                client.get("/error")

            assert "Error: GET /error" in caplog.text
            assert "Test error" in caplog.text


class TestErrorHandlerMiddleware:
    """错误处理中间件测试"""

    @pytest.fixture
    def error_handler_app(self):
        """创建带错误处理的测试应用"""
        app = FastAPI()
        app.add_middleware(ErrorHandlerMiddleware)

        @app.get("/rate_limit_error")
        async def rate_limit_endpoint():
            from app.utils.exceptions import RateLimitError
            raise RateLimitError("Too many requests")

        @app.get("/auth_error")
        async def auth_error_endpoint():
            from app.utils.exceptions import AuthenticationError
            raise AuthenticationError("Invalid credentials")

        @app.get("/unknown_error")
        async def unknown_error_endpoint():
            raise RuntimeError("Unexpected error")

        return app

    @pytest.mark.unit
    def test_handle_rate_limit_error(self, error_handler_app):
        """测试速率限制错误处理"""
        client = TestClient(error_handler_app)

        response = client.get("/rate_limit_error")
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    @pytest.mark.unit
    def test_handle_auth_error(self, error_handler_app):
        """测试认证错误处理"""
        client = TestClient(error_handler_app)

        response = client.get("/auth_error")
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.unit
    def test_handle_unknown_error(self, error_handler_app):
        """测试未知错误处理"""
        client = TestClient(error_handler_app)

        response = client.get("/unknown_error")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
