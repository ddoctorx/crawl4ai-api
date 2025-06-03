# Crawl4AI API

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Crawl4AI](https://img.shields.io/badge/Crawl4AI-0.6.2-orange)](https://github.com/unclecode/crawl4ai)

[English](#english) | [中文](#中文)

</div>

## English

A high-performance, production-ready RESTful API service built on [Crawl4AI](https://github.com/unclecode/crawl4ai), providing powerful web scraping and data extraction capabilities with modern async architecture.

### ✨ Features

- 🚀 **High Performance**: Async architecture with connection pooling for maximum throughput
- 🔧 **Multiple Crawling Modes**: Single URL, batch processing, and deep website crawling
- 🎯 **Smart Extraction**: CSS selectors and LLM-powered intelligent data extraction
- 🛡️ **Production Ready**: Rate limiting, authentication, comprehensive error handling
- 📊 **Monitoring**: Built-in health checks, metrics, and logging
- 🐳 **Docker Support**: Easy deployment with Docker and docker-compose
- 📚 **Full Documentation**: Interactive API docs with Swagger UI

### 🚀 Quick Start

#### Prerequisites

- Python 3.10+
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

#### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/crawl4ai-api.git
cd crawl4ai-api
```

2. **Install dependencies**

```bash
# Using the provided script (recommended)
./run.sh --install-only

# Or manually
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

3. **Configure environment** (optional)

```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the service**

```bash
# Using the script
./run.sh

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

### 📖 API Documentation

Once running, access the interactive documentation:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 🔌 API Endpoints

#### Core Endpoints

| Method | Endpoint            | Description            |
| ------ | ------------------- | ---------------------- |
| POST   | `/api/crawl/url`    | Crawl a single URL     |
| POST   | `/api/crawl/batch`  | Crawl multiple URLs    |
| POST   | `/api/crawl/deep`   | Deep crawl a website   |
| POST   | `/api/extract/llm`  | Extract data using LLM |
| GET    | `/api/crawl/health` | Health check           |
| GET    | `/api/version`      | API version info       |

### 💡 Usage Examples

#### Python

```python
import requests

# Crawl a single URL
response = requests.post(
    "http://127.0.0.1:8001/api/crawl/url",
    json={
        "url": "https://www.anthropic.com/engineering/building-effective-agents",
        "js_enabled": True,
        "bypass_cache": True
    }
)
result = response.json()
print(result["markdown"])
```

#### JavaScript

```javascript
// Crawl with CSS extraction
fetch('http://127.0.0.1:8001/api/crawl/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.anthropic.com/engineering/building-effective-agents',
    js_enabled: true,
    bypass_cache: true,
  }),
})
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json(); // 根据接口返回类型调整
  })
  .then(data => {
    console.log('抓取结果:', data);
  })
  .catch(error => {
    console.error('请求失败:', error);
  });
```

#### cURL

```bash
curl -X POST http://127.0.0.1:8001/api/crawl/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.anthropic.com/engineering/building-effective-agents",
    "js_enabled": true,
    "bypass_cache": true
  }'
```

```bash
# Deep crawl a website
curl -X POST http://127.0.0.1:8001/api/crawl/deep \
  -H "Content-Type: application/json" \
  -d '{
    "start_url": "https://www.anthropic.com/engineering/building-effective-agents",
    "max_depth": 2,
    "max_pages": 10,
    "include_patterns": ["*/blog/*"],
    "exclude_patterns": ["*/admin/*"]
  }'
```

### 🐳 Docker Deployment

#### Using Docker

```bash
# Build the image
docker build -t crawl4ai-api .

# Run the container
docker run -d \
  -p 8001:8001 \
  -e API_KEY_ENABLED=true \
  -e API_KEYS=your-secret-key \
  --name crawl4ai-api \
  crawl4ai-api
```

#### Using Docker Compose

```yaml
version: '3.10'

services:
  api:
    build: .
    ports:
      - '8001:8001'
    environment:
      - API_KEY_ENABLED=true
      - API_KEYS=${API_KEYS}
      - RATE_LIMIT_CALLS=100
      - RATE_LIMIT_PERIOD=60
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### 🔧 Configuration

The service can be configured via environment variables or `.env` file:

| Variable                | Description                            | Default |
| ----------------------- | -------------------------------------- | ------- |
| `PORT`                  | API service port                       | `8001`  |
| `API_KEY_ENABLED`       | Enable API key authentication          | `false` |
| `API_KEYS`              | Comma-separated list of valid API keys | `[]`    |
| `RATE_LIMIT_ENABLED`    | Enable rate limiting                   | `true`  |
| `RATE_LIMIT_CALLS`      | Max requests per period                | `100`   |
| `RATE_LIMIT_PERIOD`     | Rate limit time window (seconds)       | `60`    |
| `BROWSER_HEADLESS`      | Run browser in headless mode           | `true`  |
| `MAX_CONCURRENT_CRAWLS` | Max concurrent crawl operations        | `5`     |
| `LOG_LEVEL`             | Logging level                          | `INFO`  |

See `.env.example` for all available options.

### 🛡️ Security

#### API Key Authentication

Enable API key authentication for production:

```bash
API_KEY_ENABLED=true
API_KEYS=key1,key2,key3
```

Then include the key in requests:

```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:8001/api/crawl/url
```

#### Rate Limiting

Requests are rate-limited by default. Configure limits via:

```bash
RATE_LIMIT_CALLS=100  # requests
RATE_LIMIT_PERIOD=60  # seconds
```

#### Health Checks

```bash
curl http://localhost:8001/api/crawl/health
```

### 📋 Roadmap

- [ ] WebSocket support for real-time crawling
- [ ] Redis integration for distributed caching
- [ ] PostgreSQL storage backend
- [ ] Advanced scheduling system
- [ ] Browser session management
- [ ] Webhook notifications
- [ ] GraphQL API endpoint
- [ ] Enhanced LLM extraction strategies

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - The powerful crawling library this API is built on
- [FastAPI](https://fastapi.tiangolo.com/) - The modern web framework
- [Playwright](https://playwright.dev/) - Browser automation

---

## 中文

基于 [Crawl4AI](https://github.com/unclecode/crawl4ai) 构建的高性能、生产就绪的 RESTful API 服务，提供强大的网页爬取和数据提取功能，采用现代异步架构。

### ✨ 特性

- 🚀 **高性能**: 异步架构和连接池，实现最大吞吐量
- 🔧 **多种爬取模式**: 单个 URL、批量处理和深度网站爬取
- 🎯 **智能提取**: CSS 选择器和基于 LLM 的智能数据提取
- 🛡️ **生产就绪**: 速率限制、身份验证、全面的错误处理
- 📊 **监控支持**: 内置健康检查、指标和日志记录
- 🐳 **Docker 支持**: 使用 Docker 和 docker-compose 轻松部署
- 📚 **完整文档**: 使用 Swagger UI 的交互式 API 文档

### 🚀 快速开始

详细的安装和使用说明请参考上方的英文文档。

### 📄 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。
