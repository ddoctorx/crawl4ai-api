import os
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    # 移除非法字符
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    # 将空格替换为下划线
    sanitized = sanitized.replace(' ', '_')
    return sanitized


def format_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """格式化错误响应"""
    return {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code
        }
    }


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """获取环境变量，如果不存在则返回默认值"""
    return os.environ.get(name, default)
