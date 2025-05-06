import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import crawls, extraction

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="Crawl4AI API",
    description="基于Crawl4AI的RESTful API服务，提供网页爬取和数据提取功能。",
    version="0.1.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(crawls.router)
app.include_router(extraction.router)


@app.get("/")
async def root():
    """
    API根路径，返回基本信息
    """
    return {
        "message": "欢迎使用Crawl4AI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/api/version")
async def version():
    """
    获取API版本信息
    """
    return {
        "version": app.version,
        "title": app.title,
        "description": app.description
    }


if __name__ == "__main__":
    # 直接运行时使用uvicorn启动
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
