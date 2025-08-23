from __future__ import annotations

import os
from typing import Optional, Dict, Iterable, Any
import time
import random
import asyncio
from contextlib import asynccontextmanager

import httpx
from loguru import logger

from .models import TaxInfo, TaxLookupError, TaxNotFoundError
from .result import TaxInfoResult
from .router import TaxIDRouter
from .cache import AsyncResponseCache
from .parser import (
    extract_fields,
    map_fields,
    parse_search_results,
    parse_search_results_rows,
    has_no_results,
)


DEFAULT_BASE_URL = (
    os.getenv("PHASI_VATINFO_URL")
    or "https://vsreg.rd.go.th/VATINFOWSWeb/jsp/VATInfoWSServlet"
)


class AsyncVATInfoClient:
    """Async client for RD VATINFO service with high performance features.
    
    Features:
    - Full async/await support
    - Connection pooling with configurable limits
    - Automatic retries with exponential backoff
    - Rate limiting support
    - Request coalescing for concurrent identical requests
    - Context manager support
    
    Example:
        async with AsyncVATInfoClient() as client:
            result = await client.lookup("0107555000023")
            print(result.first.company_name)
    """
    
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 15.0,
        verify: bool = True,
        headers: Optional[Dict[str, str]] = None,
        # Connection pooling
        max_connections: int = 10,
        max_keepalive_connections: int = 5,
        keepalive_expiry: float = 5.0,
        # Robustness knobs
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_on_status: Optional[Iterable[int]] = (429, 500, 502, 503, 504),
        # Rate limiting
        min_interval: float = 0.0,
        # Request coalescing
        enable_coalescing: bool = True,
        # Response caching
        enable_cache: bool = False,
        cache_ttl: float = 300.0,  # 5 minutes default
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.verify = verify
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0 Safari/537.36"
            ),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://vsreg.rd.go.th",
            "Referer": "https://vsreg.rd.go.th/VATINFOWSWeb/jsp/VATInfoWSServlet",
            **(headers or {}),
        }
        
        # Connection pooling configuration
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify,
            headers=self.headers,
            limits=limits,
        )
        
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status = tuple(retry_on_status or ())
        self.min_interval = max(0.0, float(min_interval))
        self._next_allowed_time = 0.0
        
        # Request coalescing for concurrent identical requests
        self.enable_coalescing = enable_coalescing
        self._pending_requests: Dict[str, asyncio.Future] = {}
        
        # Router for auto-detection
        self._router = TaxIDRouter(enable_cache=True)
        
        # Response cache
        self.enable_cache = enable_cache
        self._response_cache = AsyncResponseCache(ttl=cache_ttl) if enable_cache else None
        
        logger.debug(
            "AsyncVATInfoClient initialized | base_url={} timeout={} retries={} "
            "connections={} coalescing={} cache={}",
            self.base_url,
            self.timeout,
            self.max_retries,
            max_connections,
            enable_coalescing,
            "enabled" if enable_cache else "disabled",
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the async client session."""
        logger.debug("Closing AsyncVATInfoClient session")
        await self._client.aclose()
    
    async def clear_cache(self) -> None:
        """Clear the response cache."""
        if self._response_cache:
            await self._response_cache.clear()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats or None if cache disabled
        """
        if self._response_cache:
            return await self._response_cache.get_stats()
        return {"enabled": False}
    
    async def _rate_limit_wait(self) -> None:
        """Apply rate limiting if configured."""
        if self.min_interval <= 0:
            return
        now = time.monotonic()
        if now < self._next_allowed_time:
            sleep_for = self._next_allowed_time - now
            logger.debug("Rate limiting: sleeping for {:.3f}s", sleep_for)
            await asyncio.sleep(sleep_for)
        self._next_allowed_time = time.monotonic() + self.min_interval
    
    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Send an HTTP request with retry + backoff + optional rate limiting.
        
        Retries on transient network errors and selected HTTP status codes.
        """
        last_exc: Optional[Exception] = None
        attempt = 0
        
        while attempt < max(1, self.max_retries):
            await self._rate_limit_wait()
            try:
                logger.debug(
                    "Async HTTP {} {} (attempt {}/{})",
                    method, url, attempt + 1, self.max_retries
                )
                resp = await self._client.request(method, url, **kwargs)
                
                if self.retry_on_status and resp.status_code in self.retry_on_status:
                    delay = self.backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                    logger.warning(
                        "Retryable status {} received. Backing off for {:.2f}s (attempt {}/{})",
                        resp.status_code,
                        delay,
                        attempt + 1,
                        self.max_retries,
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    last_exc = None
                    continue
                    
                logger.debug("Async HTTP {} -> {} {} bytes", method, resp.status_code, len(resp.content))
                return resp
                
            except httpx.HTTPError as e:
                last_exc = e
                delay = self.backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                if attempt + 1 >= self.max_retries:
                    logger.error("Network error after retries: {}", repr(e))
                    break
                logger.warning(
                    "Network error: {}. Backing off for {:.2f}s (attempt {}/{})",
                    repr(e),
                    delay,
                    attempt + 1,
                    self.max_retries,
                )
                await asyncio.sleep(delay)
                attempt += 1
        
        # Exhausted retries
        if last_exc:
            raise TaxLookupError(f"Network error: {last_exc}") from last_exc
        raise TaxLookupError("Request failed after retries.")
    
    async def _lookup_impl(self, tax_id: str, branch_no: Optional[str] = None) -> TaxInfo:
        """Internal implementation of single lookup."""
        # Use router for validation and form building
        routing = self._router.route(tax_id, branch_no)
        data = routing["form_data"]
        cleaned_id = routing["cleaned_id"]
        
        # Prime session (JSESSIONID) similar to a user visit
        try:
            await self._request("GET", self.base_url)
        except TaxLookupError as e:
            logger.warning("Session priming GET failed: {}", e)
        
        resp = await self._request("POST", self.base_url, data=data)
        
        # Decode TIS-620 to Unicode
        try:
            html = resp.content.decode("tis-620", errors="ignore")
        except Exception as e:
            logger.warning("Decode via tis-620 failed: {}. Using resp.text fallback", e)
            html = resp.text
        
        # Detect common not-found / not-registrant messages
        if has_no_results(html):
            logger.info("No VAT record: tax_id={} branch={}", cleaned_id, routing["branch_no"])
            raise TaxNotFoundError("No record found for the given tax ID/branch.")
        
        # Parse results
        mapped = parse_search_results(html, query_tax_id=cleaned_id)
        raw_fields = extract_fields(html)
        
        if not mapped:
            logger.debug("Structured parse empty; falling back to heuristic field mapping")
            mapped, raw_fields = map_fields(raw_fields)
        
        info = TaxInfo(
            tax_id=cleaned_id,
            tax_id_type=routing["tax_id_type"],
            branch_no=routing["branch_no"],
            raw_html=html,
            raw_fields=raw_fields,
        )
        
        # Fill known fields
        info.company_name = mapped.get("company_name")
        info.branch_name = mapped.get("branch_name")
        info.address = mapped.get("address")
        info.status = mapped.get("status")
        info.office_name = mapped.get("office_name")
        info.register_date = mapped.get("register_date")
        info.cancel_date = mapped.get("cancel_date")
        
        return info
    
    async def lookup(self, tax_id: str, branch_no: Optional[str] = None) -> TaxInfo:
        """Lookup a single tax ID with optional branch.
        
        Args:
            tax_id: Tax ID (10 or 13 digits, auto-detected)
            branch_no: Optional branch number
            
        Returns:
            TaxInfo object with the result
            
        Raises:
            TaxValidationError: If tax ID is invalid
            TaxNotFoundError: If no record found
            TaxLookupError: On network errors
        """
        # Check for request coalescing
        if self.enable_coalescing:
            cache_key = f"{tax_id}:{branch_no}"
            if cache_key in self._pending_requests:
                logger.debug(f"Coalescing request for {cache_key}")
                return await self._pending_requests[cache_key]
            
            # Create future for this request
            future = asyncio.create_task(self._lookup_impl(tax_id, branch_no))
            self._pending_requests[cache_key] = future
            
            try:
                result = await future
                return result
            finally:
                # Clean up pending request
                self._pending_requests.pop(cache_key, None)
        else:
            return await self._lookup_impl(tax_id, branch_no)
    
    async def lookup_many(self, tax_id: str, branch_no: Optional[str] = None) -> list[TaxInfo]:
        """Lookup all branches for a tax ID.
        
        Args:
            tax_id: Tax ID (10 or 13 digits, auto-detected)
            branch_no: Optional branch filter
            
        Returns:
            List of TaxInfo objects for all matching branches
            
        Raises:
            TaxValidationError: If tax ID is invalid
            TaxNotFoundError: If no records found
            TaxLookupError: On network errors
        """
        # Use router for validation and form building
        routing = self._router.route(tax_id, branch_no)
        data = routing["form_data"]
        cleaned_id = routing["cleaned_id"]
        
        try:
            await self._request("GET", self.base_url)
        except TaxLookupError as e:
            logger.warning("Session priming GET failed: {}", e)
        
        resp = await self._request("POST", self.base_url, data=data)
        
        try:
            html = resp.content.decode("tis-620", errors="ignore")
        except Exception as e:
            logger.warning("Decode via tis-620 failed: {}. Using resp.text fallback", e)
            html = resp.text
        
        # Detect common not-found / not-registrant messages early
        if has_no_results(html):
            logger.info("No VAT records for tax_id={} branch={}", cleaned_id, routing["branch_no"])
            raise TaxNotFoundError("No records found.")

        rows = parse_search_results_rows(html, query_tax_id=cleaned_id)
        raw_fields = extract_fields(html)
        
        results: list[TaxInfo] = []
        for row in rows:
            info = TaxInfo(
                tax_id=cleaned_id,
                tax_id_type=routing["tax_id_type"],
                branch_no=None,
                raw_html=None,
                raw_fields=raw_fields,
            )
            
            # Extract branch number
            bn = row.get("branch_name")
            if bn:
                bn_str = bn.strip()
                if bn_str.isdigit():
                    info.branch_no = bn_str
                elif "สำนักงานใหญ่" in bn_str:
                    info.branch_no = "0"
                else:
                    info.branch_no = None
            
            info.branch_name = row.get("branch_name")
            info.company_name = row.get("company_name")
            info.address = row.get("address")
            info.register_date = row.get("register_date")
            results.append(info)
        
        # Fallback to single lookup if no rows
        if not results:
            logger.debug("No structured rows; falling back to single lookup()")
            try:
                results.append(await self.lookup(tax_id, branch_no))
            except TaxLookupError:
                logger.info(
                    "Fallback single lookup() also failed for tax_id={} branch={}",
                    tax_id, branch_no
                )
                pass
        
        if not results:
            logger.info("No records found for tax_id={} branch={}", tax_id, branch_no)
            raise TaxNotFoundError("No records found.")
        
        return results
    
    async def lookup_smart(self, tax_id: str, branch_no: Optional[str] = None) -> TaxInfoResult:
        """Smart lookup that returns a TaxInfoResult wrapper.
        
        This method automatically handles single vs multiple results and returns
        a smart wrapper that provides a unified interface.
        
        Args:
            tax_id: Tax ID (10 or 13 digits, auto-detected)
            branch_no: Optional branch filter
            
        Returns:
            TaxInfoResult wrapper with smart accessors
            
        Raises:
            TaxValidationError: If tax ID is invalid
            TaxNotFoundError: If no records found
            TaxLookupError: On network errors
        """
        # Check cache if enabled
        if self._response_cache:
            routing = self._router.route(tax_id, branch_no)
            cache_key = f"{routing['cleaned_id']}:{routing['branch_no'] or ''}"
            cached = await self._response_cache.get(cache_key)
            if cached is not None:
                logger.info(f"Returning cached result for {cache_key}")
                return cached
        
        # Fetch from API
        try:
            results = await self.lookup_many(tax_id, branch_no)
        except TaxNotFoundError:
            routing = self._router.route(tax_id, branch_no)
            logger.info(
                "Returning empty result for tax_id={} branch={} (not found)",
                routing["cleaned_id"], routing["branch_no"]
            )
            return TaxInfoResult(results=[], query_tax_id=routing["cleaned_id"])
        routing = self._router.route(tax_id, branch_no)
        result = TaxInfoResult(results=results, query_tax_id=routing["cleaned_id"])
        
        # Cache the result if caching is enabled
        if self._response_cache:
            cache_key = f"{routing['cleaned_id']}:{routing['branch_no'] or ''}"
            await self._response_cache.set(cache_key, result)
        
        return result


async def lookup_async(
    tax_id: str,
    branch_no: Optional[str] = None,
    *,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    verify: Optional[bool] = None,
    headers: Optional[Dict[str, str]] = None,
    enable_cache: bool = False,
    cache_ttl: float = 300.0,
) -> TaxInfoResult:
    """Async unified lookup with smart result wrapper.
    
    This is the primary async API that automatically handles both single
    and multiple results, returning a smart wrapper for easy access.
    
    Args:
        tax_id: Tax ID to lookup (10 or 13 digits, auto-detected)
        branch_no: Optional branch number filter
        base_url: Override default API endpoint
        timeout: Request timeout in seconds
        verify: Whether to verify SSL certificates
        headers: Additional headers to include
        
    Returns:
        TaxInfoResult with smart accessors for single/multi results
        
    Example:
        result = await lookup_async("0107555000023")
        if result.is_single:
            print(result.company_name)
        else:
            for info in result:
                print(f"Branch {info.branch_no}: {info.company_name}")
    """
    async with AsyncVATInfoClient(
        base_url=base_url or DEFAULT_BASE_URL,
        timeout=timeout or 15.0,
        verify=True if verify is None else verify,
        headers=headers,
        enable_cache=enable_cache,
        cache_ttl=cache_ttl,
    ) as client:
        return await client.lookup_smart(tax_id, branch_no)
