from __future__ import annotations

import time
import httpx
import pytest

from phasi_kit import VATInfoClient, lookup
from phasi_kit.cache import ResponseCache, CacheEntry
from phasi_kit.result import TaxInfoResult


HTML_RESPONSE = """
<html><head><meta charset="TIS-620"></head>
<body>
  <table>
    <tr>
      <th>ลำดับ</th>
      <th>เลขประจำตัว ผู้เสียภาษีอากร</th>
      <th>สาขา</th>
      <th>ชื่อผู้ประกอบการ / ชื่อสถานประกอบการ</th>
      <th>ที่อยู่</th>
      <th>รหัส ไปรษณีย์</th>
      <th>วันที่ จดทะเบียน</th>
    </tr>
    <tr>
      <td>1</td>
      <td>3031571440 0105547127301</td>
      <td>สำนักงานใหญ่</td>
      <td>บริษัท เกษรแอสเซท แมนเนจเม้นท์ จำกัด / บริษัท เกษรแอสเซท แมนเนจเม้นท์ จำกัด</td>
      <td>เลขที่ 999 ถนน เพลินจิต ตำบล/แขวง ลุมพินี อำเภอ/เขต ปทุมวัน จังหวัด กรุงเทพมหานคร</td>
      <td>10330</td>
      <td>25/02/2553</td>
    </tr>
  </table>
</body></html>
"""


class MockTransportWithCounter(httpx.MockTransport):
    """Mock transport that counts requests."""
    
    def __init__(self, html: str):
        self.html = html
        self.request_count = 0
        super().__init__(self.handler)
    
    def handler(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        content = self.html.encode("tis-620", errors="ignore")
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html; charset=TIS-620"},
            content=content,
            request=request,
        )


def test_cache_disabled_by_default():
    """Test that cache is disabled by default."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=transport,
    )
    
    # First lookup
    result1 = client.lookup_smart("3031571440")
    assert transport.request_count == 2  # GET + POST
    
    # Second lookup - should make new requests (no cache)
    result2 = client.lookup_smart("3031571440")
    assert transport.request_count == 4  # Another GET + POST
    
    client.close()


def test_cache_enabled():
    """Test that cache works when enabled."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
        cache_ttl=60,  # 1 minute
    )
    
    # First lookup
    result1 = client.lookup_smart("3031571440")
    assert transport.request_count == 2  # GET + POST
    assert result1.first.company_name.startswith("บริษัท เกษรแอสเซท")
    
    # Second lookup - should use cache
    result2 = client.lookup_smart("3031571440")
    assert transport.request_count == 2  # No new requests
    assert result2.first.company_name == result1.first.company_name
    
    # Check cache stats
    stats = client.get_cache_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1
    
    client.close()


def test_cache_different_keys():
    """Test that different tax IDs have different cache keys."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
    )
    
    # Lookup first ID
    result1 = client.lookup_smart("3031571440")
    initial_count = transport.request_count
    
    # Lookup different ID - should make new request
    result2 = client.lookup_smart("0107555000023")
    assert transport.request_count > initial_count
    
    # Lookup first ID again - should use cache
    result3 = client.lookup_smart("3031571440")
    assert transport.request_count == transport.request_count  # No change
    
    client.close()


def test_cache_with_branch():
    """Test that branch number is part of cache key."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
    )
    
    # Lookup without branch
    result1 = client.lookup_smart("3031571440")
    count1 = transport.request_count
    
    # Lookup with branch - should make new request
    result2 = client.lookup_smart("3031571440", branch_no="0")
    assert transport.request_count > count1
    
    # Lookup with same branch - should use cache
    result3 = client.lookup_smart("3031571440", branch_no="0")
    assert transport.request_count == transport.request_count  # No change
    
    client.close()


def test_cache_clear():
    """Test clearing the cache."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
    )
    
    # Fill cache
    result1 = client.lookup_smart("3031571440")
    count1 = transport.request_count
    
    # Use cache
    result2 = client.lookup_smart("3031571440")
    assert transport.request_count == count1  # No new requests
    
    # Clear cache
    client.clear_cache()
    
    # Should make new request after clear
    result3 = client.lookup_smart("3031571440")
    assert transport.request_count > count1
    
    client.close()


def test_cache_ttl():
    """Test that cache entries expire after TTL."""
    cache = ResponseCache(ttl=0.1)  # 100ms TTL
    
    # Add entry
    cache.set("test", "value")
    assert cache.get("test") == "value"
    
    # Wait for expiration
    time.sleep(0.2)
    assert cache.get("test") is None  # Should be expired


def test_lookup_function_with_cache():
    """Test the unified lookup function with cache."""
    transport = MockTransportWithCounter(HTML_RESPONSE)
    
    # First lookup with cache
    result1 = lookup(
        "3031571440",
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
        cache_ttl=60,
    )
    count1 = transport.request_count
    
    # Second lookup - new client, no cache sharing
    result2 = lookup(
        "3031571440",
        base_url="https://example.invalid",
        transport=transport,
        enable_cache=True,
        cache_ttl=60,
    )
    assert transport.request_count > count1  # New requests (different client instance)


def test_cache_stats():
    """Test cache statistics."""
    cache = ResponseCache(ttl=300)
    
    # Initial stats
    stats = cache.get_stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["size"] == 0
    
    # Add and retrieve
    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    cache.get("key2")  # Miss
    
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1
    assert "50.0%" in stats["hit_rate"]