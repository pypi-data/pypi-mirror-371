"""
Basic tests for langchain-hreflang package.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from langchain_hreflang import (
    HreflangClient,
    HreflangAPIError,
    HreflangAuthenticationError,
    test_hreflang_urls,
    hreflang_tools,
)


class TestHreflangClient:
    """Test the HreflangClient class."""
    
    def test_client_init_with_api_key(self):
        """Test client initialization with API key."""
        client = HreflangClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://app.hreflang.org/api"
    
    def test_client_init_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {'HREFLANG_API_KEY': 'env_key'}):
            client = HreflangClient()
            assert client.api_key == "env_key"
    
    def test_client_init_no_api_key(self):
        """Test client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(HreflangAuthenticationError):
                HreflangClient()
    
    def test_submit_url_list_empty(self):
        """Test submitting empty URL list raises error."""
        client = HreflangClient(api_key="test_key")
        with pytest.raises(HreflangAPIError):
            client.submit_url_list([])
    
    def test_submit_url_list_invalid_url(self):
        """Test submitting invalid URL raises error."""
        client = HreflangClient(api_key="test_key")
        with pytest.raises(HreflangAPIError):
            client.submit_url_list(["not_a_url"])


class TestTools:
    """Test the LangChain tools."""
    
    def test_tools_list_contains_all_tools(self):
        """Test that hreflang_tools contains all expected tools."""
        assert len(hreflang_tools) == 3
        tool_names = [tool.name for tool in hreflang_tools]
        expected_names = [
            "test_hreflang_urls",
            "test_hreflang_sitemap",
            "check_hreflang_account_status"
        ]
        for name in expected_names:
            assert name in tool_names
    
    def test_tool_has_description(self):
        """Test that tools have descriptions."""
        for tool in hreflang_tools:
            assert hasattr(tool, 'description')
            assert len(tool.description) > 10  # Should have meaningful description
    
    @patch.dict(os.environ, {'HREFLANG_API_KEY': 'test_key'})
    @patch('langchain_hreflang.client.requests.Session.request')
    def test_test_hreflang_urls_tool(self, mock_request):
        """Test the test_hreflang_urls tool."""
        # Mock API responses
        mock_submit_response = MagicMock()
        mock_submit_response.status_code = 200
        mock_submit_response.json.return_value = {
            "test_id": "test123",
            "success": True,
            "status": "submitted"
        }
        
        mock_results_response = MagicMock()
        mock_results_response.status_code = 200
        mock_results_response.json.return_value = {
            "test_id": "test123",
            "test_status": "complete",
            "test_results": {
                "hreflang_map": {
                    "https://example.com/en/": {
                        "self_lang": "en",
                        "hreflangs": {"en": "https://example.com/en/"}
                    }
                },
                "return_tag_errors": [],
                "all_other_errors_and_warnings": {}
            }
        }
        
        # First call returns submit response, second returns results
        mock_request.side_effect = [mock_submit_response, mock_results_response]
        
        # Test the tool
        result = test_hreflang_urls.run("https://example.com/en/")
        
        assert "test123" in result
        assert "https://example.com/en/" in result
        assert "Self-declared language: en" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])