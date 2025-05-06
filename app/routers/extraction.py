from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional

from app.models.models import CrawlRequest, CrawlResult
from app.services.extraction_service import ExtractionService
from app.utils.helpers import is_valid_url, format_error_response

router = APIRouter(
    prefix="/api/extract",
    tags=["提取"],
    responses={404: {"description": "未找到"}},
)


@router.post("/llm", response_model=CrawlResult)
async def extract_with_llm(request: CrawlRequest):
    """
    使用LLM从网页提取结构化数据
    """
    if not is_valid_url(request.url):
        raise HTTPException(status_code=400, detail="无效的URL")

    if not request.llm_extraction:
        raise HTTPException(status_code=400, detail="LLM提取配置缺失")

    result = await ExtractionService.extract_with_llm(request)
    return result
