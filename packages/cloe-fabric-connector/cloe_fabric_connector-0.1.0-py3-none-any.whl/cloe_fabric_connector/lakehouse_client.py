import time
from typing import Any

import httpx
from cloe_logging import LoggerFactory

logger = LoggerFactory.get_logger(handler_types=["console"], filename="fabric_connector.log")


class LakehouseClientError(Exception):
    """Custom exception for LakehouseClient errors."""

    pass


class LakehouseClient:
    """Client for executing queries against Microsoft Fabric Lakehouse via Livy sessions."""

    def __init__(self, params: dict[str, Any]) -> None:
        """Initialize the LakehouseClient with session parameters."""
        self.session_url = params.get("session_url")
        self.headers = params.get("headers")
        self.client = httpx.Client()

        if not self.session_url:
            raise LakehouseClientError("session_url is required")
        if not self.headers:
            raise LakehouseClientError("headers are required")

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def _submit_query(self, query: str, kind: str = "sql") -> str:
        """Submit a query to the Livy session and return the statement ID."""
        url = f"{self.session_url}/statements"
        payload = {"code": query, "kind": kind}

        try:
            response = self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            statement_id = response.json().get("id")

            if not statement_id:
                raise LakehouseClientError("No statement ID returned from query submission")

            return str(statement_id)
        except httpx.HTTPError as e:
            raise LakehouseClientError(f"Failed to submit query: {e}") from e

    def _poll_result(self, statement_id: str, timeout: int, poll_interval: int) -> list[dict[str, Any]]:
        """Poll for query results until completion or timeout."""
        result_url = f"{self.session_url}/statements/{statement_id}"
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Query timed out after {timeout} seconds")

            try:
                logger.info("Polling for query results")
                response = self.client.get(result_url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                state = data.get("state")
                if state == "available":
                    logger.info("Received query results")
                    return self._extract_results(data)
                if state == "error":
                    error_msg = data.get("output", {}).get("evalue", "Query execution failed")
                    raise LakehouseClientError(f"Query failed: {error_msg}")

                time.sleep(poll_interval)

            except httpx.HTTPError as e:
                raise LakehouseClientError(f"Error polling results: {e}") from e

    def _extract_results(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract and format query results from API response."""
        try:
            result = data.get("output", {}).get("data", {}).get("application/json")
            if not result:
                return []

            columns = [field["name"] for field in result["schema"]["fields"]]
            return [dict(zip(columns, row, strict=False)) for row in result["data"]]
        except (KeyError, TypeError) as e:
            raise LakehouseClientError(f"Failed to extract results: {e}") from e

    def run_sql_query(self, query: str, poll_interval: int = 5, timeout: int = 180) -> list[dict[str, Any]]:
        """Execute a SQL query and return the results."""
        if not query or not query.strip():
            raise LakehouseClientError("Query cannot be empty")

        statement_id = self._submit_query(query=query.strip(), kind="sql")
        logger.info(f"SQL query running with ID: {statement_id}")
        return self._poll_result(statement_id, timeout, poll_interval)

    def run_pyspark_query(self, query: str, poll_interval: int = 5, timeout: int = 180) -> list[dict[str, Any]]:
        """Execute a PySpark query and return the results."""
        if not query or not query.strip():
            raise LakehouseClientError("Query cannot be empty")

        statement_id = self._submit_query(query=query.strip(), kind="pyspark")
        logger.info(f"PySpark query running with ID: {statement_id}")
        return self._poll_result(statement_id, timeout, poll_interval)
