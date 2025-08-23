from __future__ import annotations

import os
from typing import Optional, Dict, Iterable, Any
import time
import random

import httpx
from loguru import logger

from .models import TaxInfo, TaxLookupError, TaxNotFoundError
from .result import TaxInfoResult
from .router import TaxIDRouter
from .validators import normalize_branch
from .cache import ResponseCache
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


class VATInfoClient:
    """Enhanced client for RD VATINFO service with auto-routing and connection pooling.

    Features:
    - Auto-detection of 10 vs 13 digit tax IDs
    - Connection pooling for better performance
    - Automatic retries with exponential backoff
    - Rate limiting support
    - Smart result wrapper for unified API
    
    Notes:
    - The endpoint responds with TIS-620 encoded HTML.
    - Public `lookup` provides the new unified API.
    - Legacy `get_tax_info` maintained for backward compatibility.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 15.0,
        verify: bool = True,
        headers: Optional[Dict[str, str]] = None,
        transport: Optional[httpx.BaseTransport] = None,
        # Connection pooling
        max_connections: int = 10,
        max_keepalive_connections: int = 5,
        # Robustness knobs
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_on_status: Optional[Iterable[int]] = (429, 500, 502, 503, 504),
        # Simple client-side rate limiting: minimum seconds between requests
        min_interval: float = 0.0,
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
        )
        
        self._client = httpx.Client(
            timeout=timeout, 
            verify=verify, 
            headers=self.headers, 
            transport=transport,
            limits=limits,
        )
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status = tuple(retry_on_status or ())
        self.min_interval = max(0.0, float(min_interval))
        self._next_allowed_time = 0.0
        
        # Router for auto-detection
        self._router = TaxIDRouter(enable_cache=True)
        
        # Response cache
        self.enable_cache = enable_cache
        self._response_cache = ResponseCache(ttl=cache_ttl) if enable_cache else None

        logger.debug(
            "VATInfoClient initialized | base_url={} timeout={} retries={} backoff_factor={} "
            "min_interval={} connections={} cache={}",
            self.base_url,
            self.timeout,
            self.max_retries,
            self.backoff_factor,
            self.min_interval,
            max_connections,
            "enabled" if enable_cache else "disabled",
        )

    def close(self) -> None:
        logger.debug("Closing VATInfoClient session")
        self._client.close()
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        if self._response_cache:
            self._response_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats or None if cache disabled
        """
        if self._response_cache:
            return self._response_cache.get_stats()
        return {"enabled": False}

    def _rate_limit_wait(self) -> None:
        if self.min_interval <= 0:
            return
        now = time.monotonic()
        if now < self._next_allowed_time:
            sleep_for = self._next_allowed_time - now
            logger.debug("Rate limiting: sleeping for {:.3f}s", sleep_for)
            time.sleep(sleep_for)
        self._next_allowed_time = time.monotonic() + self.min_interval

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Send an HTTP request with retry + backoff + optional rate limiting.

        Retries on transient network errors and selected HTTP status codes.
        """
        last_exc: Optional[Exception] = None
        attempt = 0
        while attempt < max(1, self.max_retries):
            self._rate_limit_wait()
            try:
                logger.debug("HTTP {} {} (attempt {}/{})", method, url, attempt + 1, self.max_retries)
                resp = self._client.request(method, url, **kwargs)
                if self.retry_on_status and resp.status_code in self.retry_on_status:
                    # Compute backoff and retry
                    delay = self.backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                    logger.warning(
                        "Retryable status {} received. Backing off for {:.2f}s (attempt {}/{})",
                        resp.status_code,
                        delay,
                        attempt + 1,
                        self.max_retries,
                    )
                    time.sleep(delay)
                    attempt += 1
                    last_exc = None
                    continue
                logger.debug("HTTP {} -> {} {} bytes", method, resp.status_code, len(resp.content))
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
                time.sleep(delay)
                attempt += 1

        # Exhausted
        if last_exc:
            raise TaxLookupError(f"Network error: {last_exc}") from last_exc
        raise TaxLookupError("Request failed after retries.")

    def _build_form(self, tax_id: str, branch_no: Optional[str]) -> Dict[str, str]:
        """Build form data using the router for auto-detection."""
        routing = self._router.route(tax_id, branch_no)
        return routing["form_data"]

    def lookup(self, tax_id: str, branch_no: Optional[str] = None) -> TaxInfo:
        """Legacy single lookup - maintained for backward compatibility.
        
        Consider using lookup_smart() for the new unified API.
        """
        # Use router for validation and get cleaned ID
        routing = self._router.route(tax_id, branch_no)
        data = routing["form_data"]
        cleaned_id = routing["cleaned_id"]

        # Prime session (JSESSIONID) similar to a user visit
        try:
            self._request("GET", self.base_url)
        except TaxLookupError as e:
            # Non-fatal: continue to POST; server might still accept it.
            logger.warning("Session priming GET failed: {}", e)

        resp = self._request("POST", self.base_url, data=data)

        # Decode TIS-620 to Unicode
        try:
            html = resp.content.decode("tis-620", errors="ignore")
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("Decode via tis-620 failed: {}. Using resp.text fallback", e)
            html = resp.text  # best-effort

        # Detect common not-found / not-registrant messages
        if has_no_results(html):
            logger.info("No VAT record: tax_id={} branch={}", cleaned_id, routing["branch_no"])
            raise TaxNotFoundError("No record found for the given tax ID/branch.")

        # Prefer structured parse from results table
        mapped = parse_search_results(html, query_tax_id=cleaned_id)
        raw_fields = extract_fields(html)
        # If structured parse empty, fall back to heuristic mapping
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

        # Fill known fields if present
        info.company_name = mapped.get("company_name")
        info.branch_name = mapped.get("branch_name")
        info.address = mapped.get("address")
        info.status = mapped.get("status")
        info.office_name = mapped.get("office_name")
        info.register_date = mapped.get("register_date")
        info.cancel_date = mapped.get("cancel_date")

        return info

    def lookup_many(self, tax_id: str, branch_no: Optional[str] = None) -> list[TaxInfo]:
        """Legacy multi lookup - maintained for backward compatibility.
        
        Consider using lookup_smart() for the new unified API.
        """
        # Use router for validation and get cleaned ID
        routing = self._router.route(tax_id, branch_no)
        data = routing["form_data"]
        cleaned_id = routing["cleaned_id"]

        try:
            self._request("GET", self.base_url)
        except TaxLookupError as e:
            logger.warning("Session priming GET failed: {}", e)

        resp = self._request("POST", self.base_url, data=data)

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
                raw_html=None,  # omit per-row HTML to reduce memory
                raw_fields=raw_fields,  # keep page-level fields for context
            )
            # Branch number heuristic: if branch_name is all digits or equals HQ in Thai
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

        # If no structured rows, fall back to single lookup() for detail page only
        if not results:
            logger.debug("No structured rows; falling back to single lookup()")
            try:
                results.append(self.lookup(cleaned_id, branch_no))
            except TaxLookupError:
                logger.info("Fallback single lookup() also failed for tax_id={} branch={}", cleaned_id, branch_no)
                pass

        if not results:
            logger.info("No records found for tax_id={} branch={}", cleaned_id, branch_no)
            raise TaxNotFoundError("No records found.")
        return results
    
    def lookup_smart(self, tax_id: str, branch_no: Optional[str] = None) -> TaxInfoResult:
        """Smart lookup that returns a TaxInfoResult wrapper.
        
        This is the new unified API that automatically handles single vs multiple
        results and returns a smart wrapper for easy access.
        
        Args:
            tax_id: Tax ID (10 or 13 digits, auto-detected)
            branch_no: Optional branch filter
            
        Returns:
            TaxInfoResult wrapper with smart accessors
        """
        # Check cache if enabled
        if self._response_cache:
            routing = self._router.route(tax_id, branch_no)
            cache_key = f"{routing['cleaned_id']}:{routing['branch_no'] or ''}"
            cached = self._response_cache.get(cache_key)
            if cached is not None:
                logger.info(f"Returning cached result for {cache_key}")
                return cached
        
        # Fetch from API
        try:
            results = self.lookup_many(tax_id, branch_no)
        except TaxNotFoundError:
            # Return empty smart result instead of raising, for ergonomic API
            routing = self._router.route(tax_id, branch_no)
            logger.info("Returning empty result for tax_id={} branch={} (not found)", routing["cleaned_id"], routing["branch_no"])
            return TaxInfoResult(results=[], query_tax_id=routing["cleaned_id"])
        # Get the original tax_id for the result
        routing = self._router.route(tax_id, branch_no)
        result = TaxInfoResult(results=results, query_tax_id=routing["cleaned_id"])
        
        # Cache the result if caching is enabled
        if self._response_cache:
            cache_key = f"{routing['cleaned_id']}:{routing['branch_no'] or ''}"
            self._response_cache.set(cache_key, result)
        
        return result


def get_tax_info(
    tax_id: str,
    branch_no: Optional[str] = None,
    many: bool = False,
    *,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    verify: Optional[bool] = None,
    headers: Optional[Dict[str, str]] = None,
    transport: Optional[httpx.BaseTransport] = None,
) -> TaxInfo | list[TaxInfo]:
    """Unified convenience API.

    - When `many=False` (default) returns the first matching TaxInfo.
    - When `many=True` returns a list of TaxInfo items (possibly length>1).

    Example:
        first = get_tax_info("010555299XXXX")
        rows = get_tax_info("0107555000023", many=True)
    """
    client = VATInfoClient(
        base_url=base_url or DEFAULT_BASE_URL,
        timeout=timeout or 15.0,
        verify=True if verify is None else verify,
        headers=headers,
        transport=transport,
    )
    try:
        if many:
            return client.lookup_many(tax_id, branch_no)
        return client.lookup(tax_id, branch_no)
    finally:
        client.close()


def lookup(
    tax_id: str,
    branch_no: Optional[str] = None,
    *,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    verify: Optional[bool] = None,
    headers: Optional[Dict[str, str]] = None,
    transport: Optional[httpx.BaseTransport] = None,
    enable_cache: bool = False,
    cache_ttl: float = 300.0,
) -> TaxInfoResult:
    """Unified smart lookup with auto-detection and smart result wrapper.
    
    This is the primary sync API that automatically detects 10 vs 13 digit tax IDs
    and returns a smart wrapper that handles both single and multiple results.
    
    Args:
        tax_id: Tax ID to lookup (10 or 13 digits, auto-detected)
        branch_no: Optional branch number filter
        base_url: Override default API endpoint
        timeout: Request timeout in seconds
        verify: Whether to verify SSL certificates
        headers: Additional headers to include
        transport: Custom HTTP transport
        
    Returns:
        TaxInfoResult with smart accessors for single/multi results
        
    Example:
        >>> result = lookup("0107555000023")
        >>> if result.is_single:
        ...     print(result.company_name)
        ... else:
        ...     for info in result:
        ...         print(f"Branch {info.branch_no}: {info.company_name}")
        
        >>> # Or simply use first for most common case
        >>> print(result.first.company_name)
    """
    client = VATInfoClient(
        base_url=base_url or DEFAULT_BASE_URL,
        timeout=timeout or 15.0,
        verify=True if verify is None else verify,
        headers=headers,
        transport=transport,
        enable_cache=enable_cache,
        cache_ttl=cache_ttl,
    )
    try:
        return client.lookup_smart(tax_id, branch_no)
    finally:
        client.close()


def get_tax_infos(tax_id: str, branch_no: Optional[str] = None) -> list[TaxInfo]:
    """Plural API: returns all matched rows for the given tax ID.

    Example:
        rows = get_tax_infos("0107555000023")
        for r in rows:
            print(r.branch_no, r.company_name)
    """
    client = VATInfoClient()
    try:
        return client.lookup_many(tax_id, branch_no)
    finally:
        client.close()
