"""Reprompt API Client - A modern REST client for place enrichment."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Optional

import httpx

from .exceptions import RepromptAPIError
from .generated.models import (
    BatchJob,
    BatchJobStatus,
    PlaceJobResult,
)
from .iterators import JobsPaginatedIterator, PaginatedIterator

logger = logging.getLogger(__name__)

# Note: BatchJob models from generated client are immutable (frozen attrs classes)
# Access status counts via: batch.status_counts.additional_properties['pending']

# Constants
DEFAULT_BASE_URL = "https://api.repromptai.com/v1"
BATCH_PAGE_SIZE = 100  # Default page size for batches
JOB_PAGE_SIZE = 1000  # Default page size for jobs
MAX_BATCH_LIMIT = 100  # Maximum number of batches that can be fetched at once (deprecated, use BATCH_PAGE_SIZE)


def _normalize_datetime_fields(data: dict) -> dict:
    """
    Normalize datetime fields in API responses to ensure they have timezone info.

    The API sometimes returns datetime strings without timezone info, but Pydantic
    models expect timezone-aware datetimes. This function adds 'Z' (UTC) suffix
    to datetime strings that don't have timezone info.

    Args:
        data: Dictionary containing API response data

    Returns:
        Modified dictionary with normalized datetime fields
    """

    def add_timezone_if_missing(dt_string: str) -> str:
        """Add 'Z' suffix to datetime string if it doesn't have timezone info."""
        if (
            isinstance(dt_string, str)
            and not dt_string.endswith("Z")
            and "+" not in dt_string
            and "-" not in dt_string[-6:]
        ):
            return dt_string + "Z"
        return dt_string

    # Handle job_metadata.last_enriched
    if "job_metadata" in data and isinstance(data["job_metadata"], dict):
        if "last_enriched" in data["job_metadata"]:
            data["job_metadata"]["last_enriched"] = add_timezone_if_missing(data["job_metadata"]["last_enriched"])

    # Handle created_at for batches
    if "created_at" in data:
        data["created_at"] = add_timezone_if_missing(data["created_at"])

    return data


# Re-export models for other modules to import from here
__all__ = [
    "RepromptClient",
    "RepromptAPIError",
    "BatchJob",
    "BatchJobStatus",
    "PlaceJobResult",
]


class BatchesAPI:
    """Sub-API for batch operations (read-only)."""

    def __init__(self, client: "RepromptClient"):
        self._client = client
        self._client = client
        self.api_key = client.api_key

    def list_batches(self, query: str | None = None, page_size: int = BATCH_PAGE_SIZE) -> PaginatedIterator:
        """
        List batches with automatic pagination.

        Always returns an iterator that handles pagination automatically.

        Args:
            query: Optional search query to filter batches
            page_size: Page size for iterator (default: BATCH_PAGE_SIZE, max: BATCH_PAGE_SIZE)

        Returns:
            PaginatedIterator that yields all batches
        """
        # Validate page_size against maximum
        if page_size > BATCH_PAGE_SIZE:
            raise ValueError(f"Page size cannot exceed {BATCH_PAGE_SIZE}, got {page_size}")

        # Always return iterator (Google Cloud pattern)
        logger.debug("Creating batch iterator: page_size=%s, query=%s", page_size, query)
        filters = {}
        if query:
            filters["query"] = query
        return PaginatedIterator(self._list_batches_raw, page_size, client=self._client, **filters)

    def get_batch(self, batch_id: str):
        """Retrieve the detailed status of a specific batch including job IDs."""
        logger.debug("Getting batch: %s", batch_id)

        response = self._client.get(f"/place_enrichment/batches/{batch_id}")
        # The get_batch endpoint returns a different structure with job IDs grouped by status
        # It doesn't have status_counts and created_at like the list endpoint
        # For now, return the raw response as it has a different structure than BatchJob
        return response

    def get_batches(
        self,
        limit: int = BATCH_PAGE_SIZE,
        offset: int = 0,
        query: str | None = None,
    ):
        """
        Get a page of batches with direct access to response metadata.

        Args:
            limit: Maximum number of batches to return (default: BATCH_PAGE_SIZE, max: BATCH_PAGE_SIZE)
            offset: Starting offset for pagination (default: 0)
            query: Optional search query to filter batches

        Returns:
            Response with batches and pagination metadata
        """
        # Validate limit against maximum
        if limit > BATCH_PAGE_SIZE:
            raise ValueError(f"Limit cannot exceed {BATCH_PAGE_SIZE}, got {limit}")

        logger.debug("Getting batches: limit=%s, offset=%s, query=%s", limit, offset, query)
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if query is not None:
            params["query"] = query
        return self._client.get("/place_enrichment/batches", params=params)

    def _list_batches_raw(self, limit: int = BATCH_PAGE_SIZE, offset: int = 0, **filters):
        # Validate limit against maximum
        if limit > BATCH_PAGE_SIZE:
            raise ValueError(f"Limit cannot exceed {BATCH_PAGE_SIZE}, got {limit}")

        params = {"limit": limit, "offset": offset, **filters}
        response = self._client.get("/place_enrichment/batches", params=params)

        # Convert batch dicts to BatchJob objects
        if response and "batches" in response:
            batches = response["batches"]
            if batches and isinstance(batches[0], dict):
                # Normalize datetime fields for each batch
                batches = [_normalize_datetime_fields(batch) for batch in batches]
                response["batches"] = [BatchJob(**batch) for batch in batches]
        return response


class JobsAPI:
    """Sub-API for job operations (read-only)."""

    def __init__(self, client: "RepromptClient"):
        self._client = client
        self._client = client
        self.api_key = client.api_key

    def get_jobs_by_batch_id(self, batch_id: str, page_size: int = JOB_PAGE_SIZE) -> JobsPaginatedIterator:
        """
        Get all jobs for a specific batch with automatic pagination.

        Args:
            batch_id: Batch ID to get jobs for
            page_size: Page size for iterator (default: 100)

        Returns:
            JobsPaginatedIterator that yields all jobs
        """

        def fetch_jobs(limit: int, offset: int, **kwargs):  # pylint: disable=unused-argument
            logger.debug("Fetching jobs for batch %s: limit=%s, offset=%s", batch_id, limit, offset)
            params = {"limit": limit, "offset": offset, "batchId": batch_id}
            return self._client.get("/place_enrichment/jobs", params=params)

        return JobsPaginatedIterator(fetch_jobs, page_size=page_size, client=self._client)

    def get_job(self, place_id: str) -> PlaceJobResult:
        """Get job details for a specific place."""
        logger.debug("Getting job for place_id: %s", place_id)

        response = self._client.get(f"/place_enrichment/jobs/{place_id}")

        # Normalize datetime fields to ensure they have timezone info
        response = _normalize_datetime_fields(response)

        return PlaceJobResult(**response)


class RepromptClient:  # pylint: disable=too-many-instance-attributes
    """
    A read-only REST client for the Reprompt Place Enrichment API.

    This client provides read-only access to jobs and batches with proper
    error handling, parallel processing, and type safety through Pydantic models.

    Focused on listing and accessing data - no write operations supported.
    """

    def __init__(
        self,
        api_key: str | None = None,
        org_slug: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        """
        Initialize the Reprompt API client (read-only).

        Args:
            api_key: Your Reprompt API key. If not provided, tries REPROMPT_API_KEY env var
            org_slug: Organization slug (e.g., 'test-hp'). If not provided, tries REPROMPT_ORG_SLUG env var
            base_url: Base URL for the API (default: https://api.repromptai.com/v1)
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Get api_key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv("REPROMPT_API_KEY")

        if not api_key:
            raise ValueError(
                "API key is required. Provide api_key parameter or set REPROMPT_API_KEY environment variable"
            )

        # Get org_slug from parameter or environment variable
        if org_slug is None:
            org_slug = os.getenv("REPROMPT_ORG_SLUG")

        if not org_slug:
            raise ValueError(
                "Organization slug is required. Provide org_slug parameter "
                "or set REPROMPT_ORG_SLUG environment variable"
            )

        # Validate org_slug format to prevent URL injection
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,48}[a-zA-Z0-9]$", org_slug):
            raise ValueError(
                f"Invalid org_slug format: '{org_slug}'. "
                "Must be 2-50 characters, alphanumeric with hyphens, "
                "and cannot start or end with a hyphen."
            )

        self.api_key = api_key
        self.org_slug = org_slug
        self.timeout = timeout
        self.readonly = True  # Client is always read-only
        self._base_url = base_url

        # Store configuration
        self.api_key = api_key
        self.org_slug = org_slug
        self.timeout = timeout
        self.readonly = True  # Client is always read-only
        self._base_url = base_url

        # Create HTTP client with organization-specific URL
        self._full_base_url = f"{base_url.rstrip('/')}/{org_slug}"
        self._client = httpx.Client(timeout=timeout)

        # Create sub-APIs
        self.batches = BatchesAPI(self)
        self.jobs = JobsAPI(self)

        logger.debug("Initialized RepromptClient for org: %s", org_slug)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self._full_base_url}{path}"
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
        }

        # Clean params - remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        logger.debug("GET %s with params: %s", url, params)

        response = self._client.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise HTTPStatusError for bad status codes

        return response.json()

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self._base_url

    def close(self):
        """Close the underlying HTTP client."""
        if self._client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
