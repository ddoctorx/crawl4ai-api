# 测试指南

本文档介绍如何测试 Crawl4AI API 项目的代码。

## 目录

- [快速开始](#快速开始)
- [测试结构](#测试结构)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [测试覆盖率](#测试覆盖率)
- [持续集成](#持续集成)
- [测试最佳实践](#测试最佳实践)

## 快速开始

### 1. 安装测试依赖

```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装测试依赖
pip install -r requirements-test.txt

# 安装 Playwright（用于浏览器测试）
playwright install chromium
```

### 2. 运行所有测试

```bash
# 使用测试脚本（推荐）
./test.sh

# 或直接使用 pytest
pytest
```

### 3. 查看测试覆盖率

```bash
# 生成覆盖率报告
./test.sh --coverage --html

# 报告将在 htmlcov/index.html 中生成
```

## 测试结构

```
tests/
├── __init__.py
├── conftest.py              # 共享的测试配置和fixtures
├── test_crawler_service.py  # 爬虫服务单元测试
├── test_extraction_service.py # 提取服务单元测试
├── test_crawl_api.py        # 爬取API集成测试
├── test_extraction_api.py   # 提取API集成测试
├── test_middleware.py       # 中间件测试
└── test_utils.py           # 工具函数测试
```

## 运行测试

### 基本命令

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_crawler_service.py

# 运行特定测试
pytest tests/test_crawler_service.py::TestCrawlerService::test_crawl_url_success

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 使用测试脚本

```bash
# 只运行单元测试
./test.sh --unit

# 只运行集成测试
./test.sh --integration

# 运行特定标记的测试
./test.sh --mark=slow

# 监视模式（文件变化时自动重新运行）
./test.sh --watch

# 运行代码检查
./test.sh --lint

# 格式化代码
./test.sh --format
```

### 测试标记

项目中使用以下测试标记：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.requires_browser` - 需要浏览器的测试

```python
# 示例
@pytest.mark.unit
async def test_crawl_url_success():
    pass

@pytest.mark.integration
@pytest.mark.slow
async def test_deep_crawl():
    pass
```

## 编写测试

### 单元测试示例

```python
import pytest
from unittest.mock import AsyncMock, patch

from app.services.crawler_service import crawler_service
from app.models.models import CrawlRequest, CrawlResult


class TestCrawlerService:
    @pytest.mark.unit
    async def test_crawl_url_success(self, mock_async_web_crawler):
        """测试成功爬取URL"""
        # Arrange
        request = CrawlRequest(url="https://www.anthropic.com/engineering/building-effective-agents")

        # Act
        result = await crawler_service.crawl_url(request)

        # Assert
        assert result.success is True
        assert result.url == request.url
        mock_async_web_crawler.assert_called_once()
```

### 集成测试示例

```python
import pytest
from httpx import AsyncClient

from app.main import app


class TestCrawlAPI:
    @pytest.mark.integration
    async def test_crawl_endpoint(self, async_client: AsyncClient):
        """测试爬取端点"""
        response = await async_client.post(
            "/api/crawl/url",
            json={
                "url": "https://www.anthropic.com/engineering/building-effective-agents",
                "bypass_cache": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

### 使用 Fixtures

```python
# conftest.py 中定义的常用 fixtures

@pytest.fixture
def sample_crawl_request():
    """示例爬取请求"""
    return CrawlRequest(
        url="https://www.anthropic.com/engineering/building-effective-agents",
        bypass_cache=True,
        js_enabled=True
    )

@pytest.fixture
def mock_crawler():
    """Mock爬虫实例"""
    crawler = AsyncMock()
    crawler.__aenter__ = AsyncMock(return_value=crawler)
    crawler.__aexit__ = AsyncMock(return_value=None)
    return crawler
```

### Mock 外部依赖

```python
@pytest.mark.unit
async def test_with_mock(self):
    """使用Mock测试"""
    with patch("app.services.crawler_service.AsyncWebCrawler") as mock_class:
        # 配置mock行为
        mock_instance = AsyncMock()
        mock_class.return_value = mock_instance
        mock_instance.arun.return_value = MagicMock(
            success=True,
            status_code=200,
            markdown="Test content"
        )

        # 执行测试
        result = await crawler_service.crawl_url(request)

        # 验证
        assert result.success is True
```

## 测试覆盖率

### 查看覆盖率

```bash
# 终端显示覆盖率
pytest --cov=app --cov-report=term-missing

# 生成HTML报告
pytest --cov=app --cov-report=html

# 生成XML报告（用于CI）
pytest --cov=app --cov-report=xml
```

### 覆盖率目标

- 总体覆盖率: ≥ 80%
- 核心服务: ≥ 90%
- API 端点: ≥ 85%
- 工具函数: ≥ 95%

### 排除文件

在 `pytest.ini` 中配置排除规则：

```ini
[coverage:run]
omit =
    */tests/*
    */venv/*
    */__init__.py
    */config.py
```

## 持续集成

### GitHub Actions

项目使用 GitHub Actions 进行持续集成：

1. **代码质量检查** - Black, isort, Flake8, MyPy
2. **单元测试** - 快速运行的单元测试
3. **集成测试** - 包含浏览器的集成测试
4. **覆盖率报告** - 上传到 Codecov
5. **安全扫描** - Trivy 漏洞扫描

### 本地运行 CI 检查

```bash
# 运行所有 CI 检查
./test.sh --lint && ./test.sh --coverage
```

## 测试最佳实践

### 1. 测试命名

```python
# 好的命名
def test_crawl_url_returns_success_with_valid_url():
    pass

def test_crawl_url_raises_error_with_invalid_url():
    pass

# 避免
def test_crawl():  # 太模糊
    pass
```

### 2. AAA 模式

```python
async def test_example():
    # Arrange - 准备测试数据
    request = CrawlRequest(url="https://www.anthropic.com/engineering/building-effective-agents")

    # Act - 执行测试动作
    result = await service.crawl_url(request)

    # Assert - 验证结果
    assert result.success is True
```

### 3. 隔离测试

```python
# 每个测试应该独立运行
class TestService:
    def setup_method(self):
        """每个测试前运行"""
        self.service = Service()

    def teardown_method(self):
        """每个测试后运行"""
        self.service.cleanup()
```

### 4. 使用 Parametrize

```python
@pytest.mark.parametrize("url,expected", [
    ("https://www.anthropic.com/engineering/building-effective-agents", True),
    ("http://localhost", True),
    ("not-a-url", False),
    ("", False),
])
async def test_url_validation(url, expected):
    result = is_valid_url(url)
    assert result == expected
```

### 5. 测试异步代码

```python
# 使用 pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

# 或在 pytest.ini 中设置 asyncio_mode = auto
```

### 6. 测试超时

```python
@pytest.mark.timeout(30)  # 30秒超时
async def test_slow_operation():
    await slow_operation()
```

### 7. 跳过测试

```python
@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    pass

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="不支持Windows"
)
def test_unix_only():
    pass
```

## 调试测试

### 使用 pdb

```python
def test_debug():
    import pdb; pdb.set_trace()  # 断点
    result = complex_function()
    assert result == expected
```

### VS Code 调试配置

在 `.vscode/launch.json` 中添加：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "${file}"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

## 故障排除

### 常见问题

1. **Playwright 安装失败**

   ```bash
   # 手动安装系统依赖
   playwright install-deps
   ```

2. **异步测试失败**

   ```bash
   # 确保使用正确的事件循环
   pytest --asyncio-mode=auto
   ```

3. **导入错误**

   ```bash
   # 确保项目路径在 PYTHONPATH 中
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

4. **覆盖率不准确**
   ```bash
   # 清理缓存文件
   rm -rf .pytest_cache .coverage*
   ```

## 性能测试

对于性能关键的代码，使用 pytest-benchmark：

```python
def test_performance(benchmark):
    result = benchmark(expensive_function, arg1, arg2)
    assert result is not None
```

## 总结

良好的测试实践能够：

- 提高代码质量
- 减少 bug
- 便于重构
- 作为文档
- 增强信心

记住：**测试不是成本，而是投资！**
