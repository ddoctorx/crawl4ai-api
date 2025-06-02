import time
import logging
from typing import Callable, Dict
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.utils.exceptions import RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件

    基于滑动窗口算法实现API调用频率限制
    """

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests: Dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # 获取客户端标识（IP或API Key）
        client_id = self._get_client_id(request)
        now = time.time()

        # 清理过期的请求记录
        requests = self.requests[client_id]
        while requests and requests[0] < now - self.period:
            requests.popleft()

        # 检查是否超过限制
        if len(requests) >= self.calls:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": int(requests[0] + self.period - now)
                }
            )

        # 记录当前请求
        requests.append(now)

        # 添加速率限制信息到响应头
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            self.calls - len(requests))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))

        return response

    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用API Key
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        # 否则使用IP地址
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host if request.client else "unknown"


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    API密钥认证中间件
    """

    def __init__(self, app):
        super().__init__(app)
        self.excluded_paths = ["/", "/docs", "/redoc",
                               "/openapi.json", "/api/version", "/api/crawl/health"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.API_KEY_ENABLED:
            return await call_next(request)

        # 排除不需要认证的路径
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # 检查API密钥
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )

        api_key = auth_header[7:]
        if api_key not in settings.API_KEYS:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        # 将API密钥添加到请求状态中
        request.state.api_key = api_key

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # 记录响应信息
            duration = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s"
            )

            # 添加响应时间头
            response.headers["X-Response-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"- Exception: {str(e)} - Duration: {duration:.3f}s"
            )
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    全局错误处理中间件
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # FastAPI的HTTPException由FastAPI自己处理
            raise
        except RateLimitError as e:
            raise HTTPException(status_code=429, detail=str(e))
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
