class CrawlerError(Exception):
    """爬虫基础异常类"""
    pass


class InvalidURLError(CrawlerError):
    """无效URL异常"""
    pass


class RateLimitError(CrawlerError):
    """速率限制异常"""
    pass


class AuthenticationError(CrawlerError):
    """认证异常"""
    pass


class ExtractionError(CrawlerError):
    """数据提取异常"""
    pass


class BrowserError(CrawlerError):
    """浏览器相关异常"""
    pass


class TimeoutError(CrawlerError):
    """超时异常"""
    pass
