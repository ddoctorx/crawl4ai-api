import requests

# Crawl a single URL
response = requests.post(
    "http://127.0.0.1:8000/api/crawl/url",
    json={
        "url": "https://www.anthropic.com/engineering/building-effective-agents",
        "js_enabled": True,
        "bypass_cache": True
    }
)
result = response.json()
print(result["markdown"])
