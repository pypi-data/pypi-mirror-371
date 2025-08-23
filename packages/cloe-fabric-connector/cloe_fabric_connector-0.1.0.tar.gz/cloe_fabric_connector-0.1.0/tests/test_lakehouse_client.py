from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest
from cloe_fabric_connector.lakehouse_client import LakehouseClient, LakehouseClientError


class TestLakehouseClient:
    """Test cases for LakehouseClient class."""

    def test_initialization_success(self):
        """Test successful LakehouseClient initialization."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }

        client = LakehouseClient(params)

        assert client.session_url == params["session_url"]
        assert client.headers == params["headers"]
        assert isinstance(client.client, httpx.Client)

    def test_initialization_missing_session_url(self):
        """Test initialization failure when session_url is missing."""
        params = {"headers": {"Authorization": "Bearer token123"}}

        with pytest.raises(LakehouseClientError, match="session_url is required"):
            LakehouseClient(params)

    def test_initialization_missing_headers(self):
        """Test initialization failure when headers are missing."""
        params = {"session_url": "https://api.fabric.microsoft.com/sessions/123"}

        with pytest.raises(LakehouseClientError, match="headers are required"):
            LakehouseClient(params)

    def test_close(self):
        """Test client cleanup."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with patch.object(client.client, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_submit_query_success(self):
        """Test successful query submission."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"id": "statement123"}

        with patch.object(client.client, "post", return_value=mock_response) as mock_post:
            statement_id = client._submit_query("SELECT * FROM table", "sql")

        assert statement_id == "statement123"
        mock_post.assert_called_once_with(
            "https://api.fabric.microsoft.com/sessions/123/statements",
            headers={"Authorization": "Bearer token123"},
            json={"code": "SELECT * FROM table", "kind": "sql"},
        )

    def test_submit_query_no_statement_id(self):
        """Test query submission when no statement ID is returned."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # Mock response without statement ID
        mock_response = Mock()
        mock_response.json.return_value = {}

        with (
            patch.object(client.client, "post", return_value=mock_response),
            pytest.raises(LakehouseClientError, match="No statement ID returned"),
        ):
            client._submit_query("SELECT * FROM table")

    def test_submit_query_http_error(self):
        """Test query submission with HTTP error."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with (
            patch.object(client.client, "post", side_effect=httpx.HTTPError("Connection failed")),
            pytest.raises(LakehouseClientError, match="Failed to submit query"),
        ):
            client._submit_query("SELECT * FROM table")

    def test_extract_results_success(self):
        """Test successful result extraction."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        data = {
            "output": {
                "data": {
                    "application/json": {
                        "schema": {"fields": [{"name": "id"}, {"name": "name"}]},
                        "data": [[1, "Alice"], [2, "Bob"]],
                    }
                }
            }
        }

        results = client._extract_results(data)

        expected = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        assert results == expected

    def test_extract_results_empty_data(self):
        """Test result extraction with empty data."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        data: dict[str, Any] = {"output": {"data": {}}}
        results = client._extract_results(data)
        assert results == []

    def test_extract_results_malformed_data(self):
        """Test result extraction with malformed data."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # This will cause TypeError when trying to access .get() on a string
        data: dict[str, Any] = {
            "output": {
                "data": {
                    "application/json": {
                        "schema": None  # This will cause TypeError when accessing ["fields"]
                    }
                }
            }
        }

        with pytest.raises(LakehouseClientError, match="Failed to extract results"):
            client._extract_results(data)

    def test_poll_result_success(self):
        """Test successful result polling."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "state": "available",
            "output": {"data": {"application/json": {"schema": {"fields": [{"name": "count"}]}, "data": [[5]]}}},
        }

        with patch.object(client.client, "get", return_value=mock_response):
            results = client._poll_result("statement123", timeout=30, poll_interval=1)

        assert results == [{"count": 5}]

    def test_poll_result_error_state(self):
        """Test polling when query is in error state."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {"state": "error", "output": {"evalue": "SQL syntax error"}}

        with (
            patch.object(client.client, "get", return_value=mock_response),
            pytest.raises(LakehouseClientError, match="Query failed: SQL syntax error"),
        ):
            client._poll_result("statement123", timeout=30, poll_interval=1)

    def test_poll_result_timeout(self):
        """Test polling timeout."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        # Mock response that never becomes available
        mock_response = Mock()
        mock_response.json.return_value = {"state": "running"}

        with (
            patch.object(client.client, "get", return_value=mock_response),
            patch("time.sleep"),
            pytest.raises(TimeoutError, match="Query timed out after 1 seconds"),
        ):
            client._poll_result("statement123", timeout=1, poll_interval=1)

    def test_poll_result_http_error(self):
        """Test polling with HTTP error."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with (
            patch.object(client.client, "get", side_effect=httpx.HTTPError("Network error")),
            pytest.raises(LakehouseClientError, match="Error polling results"),
        ):
            client._poll_result("statement123", timeout=30, poll_interval=1)

    def test_run_sql_query_success(self):
        """Test successful SQL query execution."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        expected_results = [{"id": 1, "name": "test"}]

        with (
            patch.object(client, "_submit_query", return_value="stmt123") as mock_submit,
            patch.object(client, "_poll_result", return_value=expected_results) as mock_poll,
        ):
            results = client.run_sql_query("SELECT * FROM table")

        assert results == expected_results
        mock_submit.assert_called_once_with(query="SELECT * FROM table", kind="sql")
        mock_poll.assert_called_once_with("stmt123", 180, 5)

    def test_run_sql_query_empty_query(self):
        """Test SQL query execution with empty query."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with pytest.raises(LakehouseClientError, match="Query cannot be empty"):
            client.run_sql_query("")

    def test_run_sql_query_whitespace_only(self):
        """Test SQL query execution with whitespace-only query."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with pytest.raises(LakehouseClientError, match="Query cannot be empty"):
            client.run_sql_query("   \n\t   ")

    def test_run_pyspark_query_success(self):
        """Test successful PySpark query execution."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        expected_results = [{"count": 10}]

        with (
            patch.object(client, "_submit_query", return_value="stmt456") as mock_submit,
            patch.object(client, "_poll_result", return_value=expected_results) as mock_poll,
        ):
            results = client.run_pyspark_query("df.count()", poll_interval=2, timeout=60)

        assert results == expected_results
        mock_submit.assert_called_once_with(query="df.count()", kind="pyspark")
        mock_poll.assert_called_once_with("stmt456", 60, 2)

    def test_run_pyspark_query_empty_query(self):
        """Test PySpark query execution with empty query."""
        params = {
            "session_url": "https://api.fabric.microsoft.com/sessions/123",
            "headers": {"Authorization": "Bearer token123"},
        }
        client = LakehouseClient(params)

        with pytest.raises(LakehouseClientError, match="Query cannot be empty"):
            client.run_pyspark_query("")
