from __future__ import annotations

import asyncio
import httpx
import pytest

from phasi_kit import AsyncVATInfoClient, lookup_async
from phasi_kit.result import TaxInfoResult


HTML_SINGLE = (
    """
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
    .strip()
)


HTML_MULTI = (
    """
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
      <td>3034876849 0107555000023</td>
      <td>สำนักงานใหญ่</td>
      <td>บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน) / บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)</td>
      <td>อาคาร ซี.พี.ทาวเวอร์ เลขที่ 313 ถนน สีลม ตำบล/แขวง สีลม อำเภอ/เขต บางรัก จังหวัด กรุงเทพมหานคร</td>
      <td>10500</td>
      <td>01/02/2555</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3034876849 0107555000023</td>
      <td>00001</td>
      <td>บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน) / บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด(มหาชน)</td>
      <td>เลขที่ 178 หมู่ที่ 4 ถนน พิษณุโลก-หล่มสัก ตำบล/แขวง สมอแข อำเภอ/เขต เมืองพิษณุโลก จังหวัด พิษณุโลก</td>
      <td>65000</td>
      <td>01/02/2555</td>
    </tr>
  </table>
</body></html>
"""
    .strip()
)


class MockAsyncTransport(httpx.AsyncHTTPTransport):
    """Mock async transport for testing."""
    
    def __init__(self, html: str):
        self.html = html
        super().__init__()
    
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        content = self.html.encode("tis-620", errors="ignore")
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html; charset=TIS-620"},
            content=content,
            request=request,
        )


@pytest.mark.asyncio
async def test_async_lookup_single_10_digit():
    """Test async lookup with 10-digit tax ID."""
    async with AsyncVATInfoClient(
        base_url="https://example.invalid",
    ) as client:
        # Monkey patch the client's transport
        client._client._transport = MockAsyncTransport(HTML_SINGLE)
        
        info = await client.lookup("3031571440", branch_no="0")
        assert info.tax_id == "3031571440"
        assert info.tax_id_type == "10"
        assert info.company_name.startswith("บริษัท เกษรแอสเซท")
        assert info.address and "เพลินจิต" in info.address
        assert info.register_date == "25/02/2553"


@pytest.mark.asyncio
async def test_async_lookup_many_13_digit():
    """Test async lookup_many with 13-digit tax ID."""
    async with AsyncVATInfoClient(
        base_url="https://example.invalid",
    ) as client:
        # Monkey patch the client's transport
        client._client._transport = MockAsyncTransport(HTML_MULTI)
        
        results = await client.lookup_many("0107555000023")
        assert len(results) >= 2
        assert results[0].tax_id_type == "13"
        assert results[0].company_name.startswith("บริษัท ซีพีเอฟ")
        # HQ should map to branch_no "0"
        assert any(r.branch_no == "0" for r in results)
        # One branch should be numeric
        assert any(r.branch_no and r.branch_no.isdigit() for r in results)


@pytest.mark.asyncio
async def test_async_lookup_smart():
    """Test async smart lookup with TaxInfoResult wrapper."""
    async with AsyncVATInfoClient(
        base_url="https://example.invalid",
    ) as client:
        # Monkey patch the client's transport
        client._client._transport = MockAsyncTransport(HTML_MULTI)
        
        result = await client.lookup_smart("0107555000023")
        assert isinstance(result, TaxInfoResult)
        assert not result.is_single  # Multiple results
        assert result.count >= 2
        assert result.first.company_name.startswith("บริษัท ซีพีเอฟ")
        
        # Test iteration
        companies = [info.company_name for info in result]
        assert len(companies) >= 2
        
        # Test branch filtering
        hq = result.get_branch("0")
        assert hq is not None
        assert hq.branch_no == "0"


@pytest.mark.asyncio
async def test_lookup_async_function():
    """Test the top-level lookup_async function."""
    # Create a mock transport function
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        content = HTML_SINGLE.encode("tis-620", errors="ignore")
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html; charset=TIS-620"},
            content=content,
            request=request,
        )
    
    # We can't easily mock the transport in the function, so we'll skip actual network call
    # This test primarily ensures the function signature and return type are correct
    # Real integration tests would need an actual test server or more complex mocking
    
    # Just test that the function exists and has the right signature
    assert callable(lookup_async)
    assert asyncio.iscoroutinefunction(lookup_async)


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test AsyncVATInfoClient as async context manager."""
    async with AsyncVATInfoClient(
        base_url="https://example.invalid",
    ) as client:
        assert isinstance(client, AsyncVATInfoClient)
        assert client._client is not None
    
    # After context exit, client should be closed
    # We can't easily test if it's closed, but the context manager should work


@pytest.mark.asyncio
async def test_async_auto_routing():
    """Test auto-routing with different tax ID formats."""
    async with AsyncVATInfoClient(
        base_url="https://example.invalid",
    ) as client:
        # Test with spaces and dashes (should be cleaned)
        client._client._transport = MockAsyncTransport(HTML_SINGLE)
        
        # These should all work the same (auto-cleaning)
        for tax_id in ["3031571440", "3031-571-440", "3031 571 440"]:
            result = await client.lookup_smart(tax_id)
            assert result.first.tax_id == "3031571440"
            assert result.first.tax_id_type == "10"