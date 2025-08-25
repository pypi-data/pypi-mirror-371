"""
LangChain Hreflang Tools

A comprehensive set of LangChain tools for analyzing hreflang implementation
using the hreflang.org API. Perfect for international SEO analysis with AI agents.

Compatible with:
- LangChain agents
- CrewAI agents
- Any framework that uses LangChain tools
"""

from .tools import (
    test_hreflang_urls,
    test_hreflang_sitemap,
    check_hreflang_account_status,
    hreflang_tools,
)

from .client import HreflangClient
from .exceptions import (
    HreflangAPIError,
    HreflangAuthenticationError,
    HreflangRateLimitError,
    HreflangTestTimeoutError,
    HreflangInvalidURLError,
)

__version__ = "0.1.0"
__author__ = "Nick Jasuja"
__email__ = "nikhilesh@gmail.com"

__all__ = [
    "test_hreflang_urls",
    "test_hreflang_sitemap", 
    "check_hreflang_account_status",
    "hreflang_tools",
    "HreflangClient",
    "HreflangAPIError",
    "HreflangAuthenticationError",
    "HreflangRateLimitError", 
    "HreflangTestTimeoutError",
    "HreflangInvalidURLError",
]