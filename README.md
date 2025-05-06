# Crawl4AI API

基于 Crawl4AI 库的 RESTful API 服务，提供网页爬取和数据提取功能。

## 功能特点

- 单个 URL 爬取
- 批量 URL 爬取
- 深度网站爬取
- 基于 CSS 选择器的结构化数据提取
- 基于 LLM 的智能数据提取
- 缓存控制

## 安装

### 前提条件

- Python 3.8+
- pip

### 安装步骤

1. 克隆代码库：

```bash
git clone https://github.com/your-username/crawl4ai-api.git
cd crawl4ai-api
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 安装 Playwright 依赖：

```bash
playwright install
```

## 配置

创建`.env`文件，可以配置以下环境变量：

```
PORT=8000
```

## 运行服务

```bash
uvicorn app.main:app --reload
```

或者直接运行：

```bash
python -m app.main
```

或者使用提供的脚本：

```bash
./run.sh
```

服务默认运行在 `http://localhost:8000`

## API 文档

服务启动后，可以通过以下 URL 访问 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 端点

### 爬取 API

- `POST /api/crawl/url` - 爬取单个 URL
- `POST /api/crawl/batch` - 批量爬取多个 URL
- `POST /api/crawl/deep` - 深度爬取网站
- `GET /api/crawl/health` - 健康检查

### 提取 API

- `POST /api/extract/llm` - 使用 LLM 提取网页数据

## API 调用示例

以下是每个 API 端点的调用示例，包括请求和响应格式。

### 1. 爬取单个 URL

#### 基本爬取

```bash
# 请求
curl -X POST http://localhost:8000/api/crawl/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.anthropic.com/engineering/building-effective-agents",
    "bypass_cache": true,
    "js_enabled": true
  }'

# 响应
{
  "url": "https://www.anthropic.com/engineering/building-effective-agents",
  "success": true,
  "status_code": 200,
  "markdown": "# Building effective agents\n\nPublished Dec 19, 2024\n\nWe've worked with dozens of teams building LLM agents across industries...",
  "error_message": null,
  "media": {
    "images": [
      {"src": "https://www.anthropic.com/images/agents/workflow-diagram-1.png", "alt": "Workflow diagram"}
    ]
  },
  "links": {
    "internal": [
      {"href": "/research", "text": "Research"}
    ],
    "external": [
      {"href": "https://github.com/anthropics/cookbook", "text": "Cookbook"}
    ]
  }
}
```

#### 使用 CSS 选择器

```bash
# 请求
curl -X POST http://localhost:8000/api/crawl/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.anthropic.com/engineering/building-effective-agents",
    "bypass_cache": true,
    "css_selector": "article h2"
  }'

# 响应
{
  "url": "https://www.anthropic.com/engineering/building-effective-agents",
  "success": true,
  "status_code": 200,
  "markdown": "## What are agents?\n\n## When (and when not) to use agents\n\n## When and how to use frameworks",
  "error_message": null
}
```

#### 使用 CSS 提取模式

```bash
# 请求
curl -X POST http://localhost:8000/api/crawl/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.anthropic.com/engineering/building-effective-agents",
    "bypass_cache": true,
    "css_extraction_schema": {
      "name": "ArticleHeadings",
      "baseSelector": "article",
      "fields": [
        {
          "name": "title",
          "selector": "h1",
          "type": "text"
        },
        {
          "name": "sections",
          "selector": "h2",
          "type": "text"
        }
      ]
    }
  }'

# 响应
{
  "url": "https://www.anthropic.com/engineering/building-effective-agents",
  "success": true,
  "status_code": 200,
  "extracted_content": "[{\"title\":\"Building effective agents\",\"sections\":[\"What are agents?\",\"When (and when not) to use agents\",\"When and how to use frameworks\",\"Building blocks, workflows, and agents\",\"Combining and customizing these patterns\",\"Summary\"]}]",
  "error_message": null
}
```

### 2. 批量爬取 URLs

```bash
# 请求
curl -X POST http://localhost:8000/api/crawl/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.anthropic.com/engineering/building-effective-agents",
      "https://www.anthropic.com/research"
    ],
    "bypass_cache": true,
    "js_enabled": true
  }'

# 响应
{
  "results": [
    {
      "url": "https://www.anthropic.com/engineering/building-effective-agents",
      "success": true,
      "status_code": 200,
      "markdown": "# Building effective agents\n\nPublished Dec 19, 2024\n\nWe've worked with dozens of teams building LLM agents across industries...",
      "error_message": null
    },
    {
      "url": "https://www.anthropic.com/research",
      "success": true,
      "status_code": 200,
      "markdown": "# Research at Anthropic\n\nWe're building AI systems that are safe, beneficial, and honest...",
      "error_message": null
    }
  ]
}
```

### 3. 深度爬取网站

```bash
# 请求
curl -X POST http://localhost:8000/api/crawl/deep \
  -H "Content-Type: application/json" \
  -d '{
    "start_url": "https://www.anthropic.com/engineering",
    "max_depth": 1,
    "max_pages": 5,
    "include_patterns": ["*engineering*"],
    "exclude_patterns": ["*login*", "*pricing*"],
    "bypass_cache": true
  }'

# 响应
{
  "results": [
    {
      "url": "https://www.anthropic.com/engineering",
      "success": true,
      "status_code": 200,
      "markdown": "# Engineering at Anthropic\n\nExplore our technical blog posts...",
      "error_message": null
    },
    {
      "url": "https://www.anthropic.com/engineering/building-effective-agents",
      "success": true,
      "status_code": 200,
      "markdown": "# Building effective agents\n\nPublished Dec 19, 2024...",
      "error_message": null
    },
    {
      "url": "https://www.anthropic.com/engineering/responsible-scaling",
      "success": true,
      "status_code": 200,
      "markdown": "# Responsible Scaling\n\nOur approach to scaling AI systems...",
      "error_message": null
    }
  ]
}
```

### 4. 使用 LLM 提取网页数据

```bash
# 请求
curl -X POST http://localhost:8000/api/extract/llm \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.anthropic.com/engineering/building-effective-agents",
    "bypass_cache": true,
    "llm_extraction": {
      "schema_data": {
        "title": "ArticleData",
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "publish_date": {"type": "string"},
          "main_points": {"type": "array", "items": {"type": "string"}},
          "workflows": {"type": "array", "items": {"type": "string"}}
        }
      },
      "instruction": "提取这篇关于AI agents的文章的标题、发布日期、主要观点和提到的工作流类型",
      "llm_config": {
        "provider": "openai/gpt-4o-mini",
        "api_token": "YOUR_API_KEY"
      }
    }
  }'

# 响应
{
  "url": "https://www.anthropic.com/engineering/building-effective-agents",
  "success": true,
  "status_code": 200,
  "extracted_content": "{\"title\":\"Building effective agents\",\"publish_date\":\"Dec 19, 2024\",\"main_points\":[\"最成功的实现使用简单、可组合的模式而非复杂框架\",\"应从最简单的解决方案开始，仅在需要时增加复杂性\"],\"workflows\":[\"Prompt chaining（提示链接）\",\"Routing（路由）\",\"Parallelization（并行化）\",\"Orchestrator-workers（编排者-工作者）\",\"Evaluator-optimizer（评估者-优化者）\"]}",
  "error_message": null
}
```

### 5. 健康检查

```bash
# 请求
curl http://localhost:8000/api/crawl/health

# 响应
{
  "status": "健康",
  "service": "crawl4ai-api"
}
```

## JavaScript 调用示例

### 爬取单个 URL (使用 fetch)

```javascript
fetch('http://localhost:8000/api/crawl/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.anthropic.com/engineering/building-effective-agents',
    bypass_cache: true,
    js_enabled: true,
  }),
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### 健康检查

```javascript
fetch('http://localhost:8000/api/crawl/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Docker 部署

构建 Docker 镜像：

```bash
docker build -t crawl4ai-api .
```

运行容器：

```bash
docker run -d -p 8000:8000 --name crawl4ai-api crawl4ai-api
```

## 许可证

MIT
