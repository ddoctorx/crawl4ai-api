from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional

from app.models.models import (
    CrawlRequest,
    CrawlBatchRequest,
    DeepCrawlRequest,
    CrawlResult,
    CrawlResponse
)
from app.services.crawler_service import CrawlerService
from app.utils.helpers import is_valid_url, format_error_response

router = APIRouter(
    prefix="/api/crawl",
    tags=["爬取"],
    responses={404: {"description": "未找到"}},
)


@router.post("/url", response_model=CrawlResult)
async def crawl_single_url(request: CrawlRequest):
    """
    爬取单个URL并返回结果
    """
    if not is_valid_url(request.url):
        raise HTTPException(status_code=400, detail="无效的URL")

    result = await CrawlerService.crawl_url(request)
    return result


@router.post("/batch", response_model=CrawlResponse)
async def crawl_multiple_urls(request: CrawlBatchRequest):
    """
    批量爬取URL并返回结果
    """
    # 验证URL
    invalid_urls = [url for url in request.urls if not is_valid_url(url)]
    if invalid_urls:
        raise HTTPException(
            status_code=400,
            detail=f"包含无效URL: {', '.join(invalid_urls)}"
        )

    results = await CrawlerService.crawl_multiple_urls(request)
    return CrawlResponse(results=results)


@router.post("/deep", response_model=CrawlResponse)
async def deep_crawl(request: DeepCrawlRequest):
    """
    深度爬取网站并返回结果
    """
    if not is_valid_url(request.start_url):
        raise HTTPException(status_code=400, detail="无效的起始URL")

    results = await CrawlerService.deep_crawl(request)
    return CrawlResponse(results=results)


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "健康", "service": "crawl4ai-api"}
