"""
Client for interacting with the hreflang.org API.
"""

import os
import requests
import time
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv is optional

from .exceptions import (
    HreflangAPIError,
    HreflangAuthenticationError,
    HreflangRateLimitError,
    HreflangTestTimeoutError,
    HreflangInvalidURLError,
)


class HreflangClient:
    """
    Client for interacting with the hreflang.org API.
    
    This client handles all API interactions including authentication,
    rate limiting, and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Hreflang API client.
        
        Args:
            api_key: API key for hreflang.org. If not provided, 
                    will try to get from HREFLANG_API_KEY environment variable.
        
        Raises:
            HreflangAuthenticationError: If no API key is provided or found.
        """
        self.api_key = api_key or os.getenv("HREFLANG_API_KEY")
        if not self.api_key:
            raise HreflangAuthenticationError(
                "HREFLANG_API_KEY environment variable is required. "
                "Get your API key from https://app.hreflang.org/"
            )
        
        self.base_url = "https://app.hreflang.org/api"
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a request to the hreflang.org API.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            **kwargs: Additional arguments for the request
            
        Returns:
            JSON response data
            
        Raises:
            HreflangAPIError: For various API errors
            HreflangAuthenticationError: For authentication issues
            HreflangRateLimitError: For rate limit issues
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key to parameters
        if method.upper() == "GET":
            params = kwargs.get("params", {})
            params["key"] = self.api_key
            kwargs["params"] = params
        else:
            data = kwargs.get("data", {})
            data["key"] = self.api_key
            kwargs["data"] = data
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            # Handle specific HTTP status codes
            if response.status_code == 403:
                raise HreflangAuthenticationError(
                    "Invalid API key or access denied. Check your API key at https://app.hreflang.org/"
                )
            elif response.status_code == 429:
                raise HreflangRateLimitError(
                    "API rate limit exceeded. Check your account limits or upgrade your plan."
                )
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", "Bad request - invalid parameters")
                raise HreflangInvalidURLError(error_msg)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise HreflangAPIError("Request timeout - API took too long to respond")
        except requests.exceptions.ConnectionError:
            raise HreflangAPIError("Connection error - unable to reach hreflang.org API")
        except requests.exceptions.HTTPError as e:
            raise HreflangAPIError(f"HTTP error {response.status_code}: {str(e)}")
        except ValueError as e:
            raise HreflangAPIError(f"Invalid JSON response from API: {str(e)}")
    
    def submit_url_list(self, url_list: List[str]) -> Dict[str, Any]:
        """
        Submit a list of URLs for hreflang testing.
        
        Args:
            url_list: List of URLs to test
            
        Returns:
            API response with test_id and status
        """
        if not url_list:
            raise HreflangInvalidURLError("URL list cannot be empty")
        
        # Validate URLs
        for url in url_list:
            if not url.strip() or not (url.startswith('http://') or url.startswith('https://')):
                raise HreflangInvalidURLError(f"Invalid URL: {url}")
        
        url_list_str = "\n".join(url_list)
        return self._make_request(
            "POST", 
            "test/submit/urllist",
            data={"url_list": url_list_str}
        )
    
    def submit_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """
        Submit a sitemap URL for hreflang testing.
        
        Args:
            sitemap_url: URL of the XML sitemap to test
            
        Returns:
            API response with test_id and status
        """
        if not sitemap_url or not (sitemap_url.startswith('http://') or sitemap_url.startswith('https://')):
            raise HreflangInvalidURLError(f"Invalid sitemap URL: {sitemap_url}")
        
        return self._make_request(
            "POST",
            "test/submit/sitemap", 
            data={"sitemap": sitemap_url}
        )
    
    def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """
        Get the status of a test.
        
        Args:
            test_id: Test ID returned from submit endpoint
            
        Returns:
            Test status information
        """
        if not test_id:
            raise HreflangAPIError("Test ID is required")
        
        return self._make_request(
            "GET",
            "test/status",
            params={"test_id": test_id}
        )
    
    def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed test.
        
        Args:
            test_id: Test ID returned from submit endpoint
            
        Returns:
            Complete test results
        """
        if not test_id:
            raise HreflangAPIError("Test ID is required")
        
        return self._make_request(
            "GET",
            "test/results",
            params={"test_id": test_id}
        )
    
    def get_account_limits(self) -> Dict[str, Any]:
        """
        Get account limits and usage quotas.
        
        Returns:
            Account limits information
        """
        return self._make_request("GET", "account/limits")
    
    def get_test_history(self) -> Dict[str, Any]:
        """
        Get list of recent tests.
        
        Returns:
            List of recent tests
        """
        return self._make_request("GET", "account/tests")
    
    def wait_for_test_completion(
        self, 
        test_id: str, 
        max_wait_time: int = 300, 
        check_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for a test to complete and return results.
        
        Args:
            test_id: Test ID to wait for
            max_wait_time: Maximum time to wait in seconds (default: 300)
            check_interval: How often to check status in seconds (default: 10)
            
        Returns:
            Complete test results when finished
            
        Raises:
            HreflangTestTimeoutError: If test doesn't complete within max_wait_time
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_response = self.get_test_status(test_id)
            test_status = status_response.get("test_status")
            
            if test_status == "complete":
                return self.get_test_results(test_id)
            elif test_status in ["submitted", "pending"]:
                time.sleep(check_interval)
                continue
            else:
                raise HreflangAPIError(f"Test failed with status: {test_status}")
        
        raise HreflangTestTimeoutError(
            f"Test {test_id} did not complete within {max_wait_time} seconds"
        )
    
    def __del__(self):
        """Close the session when client is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()