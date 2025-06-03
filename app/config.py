from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    应用配置管理

    使用环境变量或.env文件配置应用参数
    """

    # 基础配置
    APP_NAME: str = "Crawl4AI API"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # 浏览器配置
    BROWSER_HEADLESS: bool = True
    VIEWPORT_WIDTH: int = 1280
    VIEWPORT_HEIGHT: int = 800
    BROWSER_EXTRA_ARGS: List[str] = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-blink-features=AutomationControlled",  # 反检测
        # 真实UA
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--accept-lang=en-US,en;q=0.9",
        "--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "--ignore-certificate-errors",  # 忽略证书错误
        "--ignore-ssl-errors",
        "--ignore-certificate-errors-spki-list",
        "--disable-extensions",
        "--no-first-run",
        "--disable-default-apps"
    ]

    # 爬虫配置
    PAGE_TIMEOUT: int = 60000  # 60秒
    WAIT_FOR_IMAGES: bool = False
    MAX_CONCURRENT_CRAWLS: int = 5
    CRAWLER_POOL_SIZE: int = 10

    # 速率限制
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 秒

    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1小时

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None

    # API密钥（用于LLM提取等功能）
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"  # 生产环境请更改
    API_KEY_ENABLED: bool = False
    API_KEYS: List[str] = []

    # 数据库配置（未来扩展）
    DATABASE_URL: Optional[str] = None

    # Redis配置（用于缓存和任务队列）
    REDIS_URL: Optional[str] = None

    # 监控配置
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_log_config(self):
        """获取日志配置"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console"]
            }
        }


# 创建全局配置实例
settings = Settings()
