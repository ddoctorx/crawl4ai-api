# Contributing to Crawl4AI API

First off, thank you for considering contributing to Crawl4AI API! It's people like you that make this project better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your contribution
4. Make your changes
5. Push to your fork and submit a pull request

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Any possible drawbacks
- Examples of how the enhancement would be used

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues good for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for testing deployment)

### Setting Up Your Development Environment

1. **Clone your fork**

   ```bash
   git clone https://github.com/your-username/crawl4ai-api.git
   cd crawl4ai-api
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   playwright install chromium
   ```

4. **Set up pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Create a test configuration**
   ```bash
   cp .env.example .env.test
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_crawler_service.py

# Run with verbose output
pytest -v
```

### Running the Development Server

```bash
# With auto-reload
uvicorn app.main:app --reload

# With custom settings
uvicorn app.main:app --reload --port 8001
```

## Style Guidelines

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use type hints for all function signatures
- Use docstrings for all public functions and classes

### Code Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Run linting
flake8 app tests
mypy app
```

### Documentation

- Use clear, concise docstrings
- Include examples in docstrings where helpful
- Keep README and API documentation up to date

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(crawler): add support for custom headers
fix(rate-limit): correct window calculation
docs(api): update extraction endpoint examples
```

## Pull Request Process

1. **Before submitting:**

   - Ensure all tests pass
   - Update documentation if needed
   - Add tests for new functionality
   - Run formatting and linting tools

2. **PR Description:**

   - Reference any related issues
   - Describe what changes were made
   - Explain why the changes were necessary
   - Include screenshots for UI changes

3. **Review Process:**

   - At least one maintainer review required
   - All CI checks must pass
   - Address all review comments
   - Keep PR focused and reasonably sized

4. **After Merge:**
   - Delete your feature branch
   - Update your local main branch
   - Celebrate your contribution! 🎉

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common test data
- Mock external dependencies

### Test Structure

```python
# tests/test_feature.py
import pytest
from app.services import FeatureService

class TestFeature:
    @pytest.fixture
    def service(self):
        return FeatureService()

    def test_feature_behavior(self, service):
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = service.process(input_data)

        # Assert
        assert result.success is True
```

## Documentation

### API Documentation

- Update OpenAPI schemas when changing endpoints
- Include request/response examples
- Document all parameters and their constraints

### Code Documentation

```python
def crawl_url(self, request: CrawlRequest) -> CrawlResult:
    """
    Crawl a single URL and return structured data.

    Args:
        request: The crawl request containing URL and options

    Returns:
        CrawlResult: The crawling result with extracted data

    Raises:
        InvalidURLError: If the URL is malformed
        TimeoutError: If the crawl exceeds timeout

    Example:
        >>> request = CrawlRequest(url="https://www.anthropic.com/engineering/building-effective-agents")
        >>> result = crawler.crawl_url(request)
        >>> print(result.markdown)
    """
```

## Release Process

1. Update version in `app/config.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release PR
4. After merge, tag the release
5. GitHub Actions will handle the rest

## Community

- **Discord**: [Join our server](https://discord.gg/your-invite)
- **Discussions**: Use GitHub Discussions for questions
- **Twitter**: Follow [@YourHandle](https://twitter.com/yourhandle)

## Recognition

Contributors will be recognized in:

- The README.md contributors section
- Release notes
- Our website (coming soon)

Thank you for contributing to Crawl4AI API! 🙏
