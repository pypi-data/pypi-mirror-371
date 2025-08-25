"""
LangChain tools for hreflang SEO analysis using hreflang.org API.

This module provides three LangChain tools that can be used with AI agents
to analyze international website hreflang implementations.
"""

from langchain.tools import tool
from .client import HreflangClient
from .exceptions import HreflangAPIError


def _get_hreflang_client():
    """Get a configured Hreflang API client."""
    return HreflangClient()


@tool
def test_hreflang_urls(urls: str) -> str:
    """Test a list of URLs for hreflang implementation.
    
    This tool submits URLs to the hreflang.org API and waits for results.
    Useful for analyzing international SEO implementation.
    
    Args:
        urls: Comma-separated or newline-separated list of URLs to test
    
    Returns:
        A summary of hreflang test results including errors and warnings
    """
    try:
        client = _get_hreflang_client()
        
        # Parse URL list
        if "," in urls:
            url_list = [url.strip() for url in urls.split(",")]
        else:
            url_list = [url.strip() for url in urls.split("\n")]
        
        url_list = [url for url in url_list if url]  # Remove empty strings
        
        if not url_list:
            return "Error: No valid URLs provided"
        
        # Submit test
        submit_response = client.submit_url_list(url_list)
        test_id = submit_response.get("test_id")
        
        if not test_id:
            return f"Error submitting test: {submit_response}"
        
        # Wait for completion and get results
        results = client.wait_for_test_completion(test_id, max_wait_time=120)
        
        # Format results
        test_results = results.get("test_results", {})
        hreflang_map = test_results.get("hreflang_map", {})
        return_tag_errors = test_results.get("return_tag_errors", [])
        other_errors = test_results.get("all_other_errors_and_warnings", {})
        
        summary = []
        summary.append(f"Hreflang Test Results (Test ID: {test_id})")
        summary.append(f"Total URLs tested: {len(hreflang_map)}")
        summary.append("")
        
        # Analyze hreflang implementation
        for url, data in hreflang_map.items():
            summary.append(f"URL: {url}")
            self_lang = data.get("self_lang", "")
            hreflangs = data.get("hreflangs", {})
            
            if self_lang:
                summary.append(f"  Self-declared language: {self_lang}")
            else:
                summary.append("  ⚠️  No self-declared language found")
            
            if hreflangs:
                summary.append(f"  Hreflang links found: {len(hreflangs)}")
                for lang, link_url in hreflangs.items():
                    summary.append(f"    {lang}: {link_url}")
            else:
                summary.append("  ⚠️  No hreflang links found")
            
            summary.append("")
        
        # Add errors and warnings
        if return_tag_errors:
            summary.append("Return Tag Errors:")
            for error in return_tag_errors:
                summary.append(f"  - {error}")
            summary.append("")
        
        if other_errors:
            summary.append("Other Issues:")
            for url, issues in other_errors.items():
                if issues.get("errors") or issues.get("warnings"):
                    summary.append(f"  {url}:")
                    for error in issues.get("errors", []):
                        summary.append(f"    ❌ {error}")
                    for warning in issues.get("warnings", []):
                        summary.append(f"    ⚠️  {warning}")
            summary.append("")
        
        return "\n".join(summary)
        
    except HreflangAPIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error testing URLs: {str(e)}"


@tool 
def test_hreflang_sitemap(sitemap_url: str) -> str:
    """Test all URLs in a sitemap for hreflang implementation.
    
    This tool submits a sitemap URL to the hreflang.org API and analyzes
    the hreflang implementation across all URLs in the sitemap.
    
    Args:
        sitemap_url: URL of the XML sitemap to test
        
    Returns:
        A summary of hreflang test results for the entire sitemap
    """
    try:
        client = _get_hreflang_client()
        
        # Submit sitemap test
        submit_response = client.submit_sitemap(sitemap_url)
        test_id = submit_response.get("test_id")
        
        if not test_id:
            return f"Error submitting sitemap test: {submit_response}"
        
        # Wait for completion
        results = client.wait_for_test_completion(test_id, max_wait_time=300)
        
        # Format results
        test_results = results.get("test_results", {})
        hreflang_map = test_results.get("hreflang_map", {})
        return_tag_errors = test_results.get("return_tag_errors", [])
        other_errors = test_results.get("all_other_errors_and_warnings", {})
        
        # Create summary
        total_urls = len(hreflang_map)
        urls_with_hreflang = sum(1 for data in hreflang_map.values() if data.get("hreflangs"))
        urls_with_self_lang = sum(1 for data in hreflang_map.values() if data.get("self_lang"))
        
        summary = []
        summary.append(f"Sitemap Hreflang Analysis (Test ID: {test_id})")
        summary.append(f"Sitemap URL: {sitemap_url}")
        summary.append(f"Total URLs found: {total_urls}")
        summary.append(f"URLs with hreflang tags: {urls_with_hreflang} ({urls_with_hreflang/total_urls*100:.1f}%)" if total_urls > 0 else "URLs with hreflang tags: 0")
        summary.append(f"URLs with self-declared language: {urls_with_self_lang} ({urls_with_self_lang/total_urls*100:.1f}%)" if total_urls > 0 else "URLs with self-declared language: 0")
        summary.append("")
        
        # Language analysis
        languages = {}
        for data in hreflang_map.values():
            if data.get("hreflangs"):
                for lang in data["hreflangs"].keys():
                    languages[lang] = languages.get(lang, 0) + 1
        
        if languages:
            summary.append("Languages found:")
            for lang, count in sorted(languages.items()):
                summary.append(f"  {lang}: {count} URLs")
            summary.append("")
        
        # Show issues if any
        total_errors = len(return_tag_errors) + sum(len(issues.get("errors", [])) for issues in other_errors.values())
        total_warnings = sum(len(issues.get("warnings", [])) for issues in other_errors.values())
        
        if total_errors > 0 or total_warnings > 0:
            summary.append(f"Issues found: {total_errors} errors, {total_warnings} warnings")
            
            if return_tag_errors:
                summary.append("Return tag errors:")
                for error in return_tag_errors[:5]:  # Show first 5
                    summary.append(f"  - {error}")
                if len(return_tag_errors) > 5:
                    summary.append(f"  ... and {len(return_tag_errors) - 5} more")
        else:
            summary.append("✅ No critical issues found!")
        
        return "\n".join(summary)
        
    except HreflangAPIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error testing sitemap: {str(e)}"


@tool
def check_hreflang_account_status(input: str = "") -> str:
    """Check your hreflang.org account limits and recent test history.
    
    Args:
        input: Not used, but required for LangChain compatibility
    
    Returns information about your API usage limits and recent tests.
    """
    try:
        client = _get_hreflang_client()
        
        # Get account limits
        limits = client.get_account_limits()
        
        # Get test history
        history = client.get_test_history()
        
        summary = []
        summary.append("Hreflang.org Account Status")
        summary.append("=" * 30)
        summary.append(f"URLs per test limit: {limits.get('limit_urls_per_test', 'N/A')}")
        summary.append(f"Tests per day limit: {limits.get('limit_tests_per_day', 'N/A')}")
        summary.append("")
        
        tests = history.get("tests", [])
        if tests:
            summary.append(f"Recent tests ({len(tests)} shown):")
            for test in tests[:5]:  # Show last 5 tests
                summary.append(f"  Test ID: {test.get('test_id', 'N/A')}")
                summary.append(f"  Status: {test.get('test_status', 'N/A')}")
                summary.append(f"  Submitted: {test.get('submitted_at', 'N/A')}")
                summary.append(f"  Pages tested: {test.get('num_pages_in_test', 'N/A')}")
                summary.append("")
        else:
            summary.append("No recent tests found.")
        
        return "\n".join(summary)
        
    except HreflangAPIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error checking account status: {str(e)}"


# Export all tools for easy use
hreflang_tools = [
    test_hreflang_urls,
    test_hreflang_sitemap,
    check_hreflang_account_status
]