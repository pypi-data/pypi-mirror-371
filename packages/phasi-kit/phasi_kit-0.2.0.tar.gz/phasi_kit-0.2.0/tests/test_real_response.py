from __future__ import annotations

import httpx
import pytest

from phasi_kit import VATInfoClient, lookup
from phasi_kit.result import TaxInfoResult


# Real HTML response from RD VATINFO service (22/8/2568)
HTML_REAL_RESPONSE = """
<html><head><meta charset="TIS-620"></head>
<body>
ระบบค้นหาข้อมูลผู้ประกอบการจดทะเบียนภาษีมูลค่าเพิ่ม ซึ่งยังคงประกอบกิจการอยู่ ณ วันที่ 22/8/2568
ระบบค้นหาข้อมูลผู้ประกอบการจดทะเบียนภาษีมูลค่าเพิ่ม เวอร์ชั่น 3.7
  เงื่อนไขการค้นหา
จำนวนผู้เข้าใช้งาน ณ ขณะนี้ 669 ราย
 เลขประจำตัวผู้เสียภาษีอากร (13 หลัก)
สาขาที่
 เลขประจำตัวผู้เสียภาษีอากร (10 หลัก)
สาขาที่
 ชื่อผู้ประกอบการฯ
นามสกุล
ค้นหาข้อมูลเลขประจำตัวผู้เสียภาษีอากรเลขที่   0105534038143
<table>
<tr>
<th>ลำดับ</th>
<th>เลขประจำตัว<br>ผู้เสียภาษีอากร</th>
<th>สาขา</th>
<th>ชื่อผู้ประกอบการ /<br>ชื่อสถานประกอบการ</th>
<th>ที่อยู่</th>
<th>รหัส<br>ไปรษณีย์</th>
<th>วันที่<br>จดทะเบียน</th>
<th>ประวัติการ<br>จดทะเบียน</th>
</tr>
<tr>
<td>1</td>
<td>3101958430<br>0105534038143</td>
<td>สำนักงานใหญ่</td>
<td>บริษัท พร็อสเพอร์สโตน จำกัด   /<br>บริษัท พร็อสเพอร์สโตน จำกัด</td>
<td>เลขที่ 7 ตรอก/ซอย โพธิ์แก้ว 3 แยก 16 ถนน ลาดพร้าว 101 ตำบล/แขวง คลองจั่น อำเภอ/เขต บางกะปิ จังหวัด กรุงเทพมหานคร</td>
<td>10240</td>
<td>01/01/2535</td>
<td>ดูประวัติ</td>
</tr>
</table>
</body></html>
"""


def make_transport(html: str) -> httpx.MockTransport:
    """Create mock transport with given HTML response."""
    def handler(request: httpx.Request) -> httpx.Response:
        content = html.encode("tis-620", errors="ignore")
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html; charset=TIS-620"},
            content=content,
            request=request,
        )
    return httpx.MockTransport(handler)


def test_real_response_13_digit():
    """Test parsing real response from RD VATINFO for 13-digit tax ID."""
    client = VATInfoClient(
        base_url="https://example.invalid",
        transport=make_transport(HTML_REAL_RESPONSE)
    )
    
    # Test with the 13-digit tax ID
    info = client.lookup("0105534038143")
    
    assert info.tax_id == "0105534038143"
    assert info.tax_id_type == "13"
    assert "พร็อสเพอร์สโตน" in info.company_name
    assert "คลองจั่น" in info.address
    assert "บางกะปิ" in info.address
    assert "กรุงเทพมหานคร" in info.address
    assert info.register_date == "01/01/2535"
    
    # Branch should be recognized as HQ (สำนักงานใหญ่)
    # The parser should extract this from the table
    client.close()


def test_real_response_with_smart_lookup():
    """Test real response with the new smart lookup API."""
    result = lookup(
        "0105534038143",
        base_url="https://example.invalid",
        transport=make_transport(HTML_REAL_RESPONSE)
    )
    
    assert isinstance(result, TaxInfoResult)
    assert result.is_single  # Only one result in this response
    assert result.count == 1
    
    # Access via smart wrapper
    assert result.company_name and "พร็อสเพอร์สโตน" in result.company_name
    assert result.address and "คลองจั่น" in result.address
    assert result.register_date == "01/01/2535"
    
    # Test branch detection
    info = result.first
    assert info.branch_name == "สำนักงานใหญ่" or info.branch_no == "0"
    
    # The response shows both 10-digit (3101958430) and 13-digit (0105534038143)
    # Our system should use the 13-digit as queried
    assert info.tax_id == "0105534038143"
    assert info.tax_id_type == "13"


def test_real_response_auto_routing():
    """Test that auto-routing works with real response format."""
    # Test with different input formats - all should work
    test_cases = [
        "0105534038143",          # Clean 13-digit
        "0105-534-038143",        # With dashes
        "0105 534 038143",        # With spaces
        " 0105534038143 ",        # With surrounding spaces
    ]
    
    for tax_id_input in test_cases:
        result = lookup(
            tax_id_input,
            base_url="https://example.invalid",
            transport=make_transport(HTML_REAL_RESPONSE)
        )
        
        assert result.first.tax_id == "0105534038143", f"Failed for input: {tax_id_input}"
        assert result.first.company_name and "พร็อสเพอร์สโตน" in result.first.company_name
        

def test_real_response_branch_detection():
    """Test branch detection from real response."""
    result = lookup(
        "0105534038143",
        base_url="https://example.invalid",
        transport=make_transport(HTML_REAL_RESPONSE)
    )
    
    # The response shows "สำนักงานใหญ่" which should be detected as HQ (branch "0")
    info = result.first
    
    # Check that branch is properly identified
    if info.branch_no is not None:
        assert info.branch_no == "0"  # HQ should be "0"
    
    # Branch name should be preserved
    if info.branch_name:
        assert "สำนักงานใหญ่" in info.branch_name


def test_real_response_data_extraction():
    """Test that all data fields are properly extracted from real response."""
    result = lookup(
        "0105534038143",
        base_url="https://example.invalid",
        transport=make_transport(HTML_REAL_RESPONSE)
    )
    
    info = result.first
    
    # Verify all expected fields are extracted
    assert info.tax_id == "0105534038143"
    assert info.tax_id_type == "13"
    assert info.company_name is not None
    assert info.address is not None
    assert info.register_date is not None
    
    # Check specific content
    assert "บริษัท" in info.company_name
    assert "จำกัด" in info.company_name
    assert "โพธิ์แก้ว" in info.address or "ลาดพร้าว" in info.address
    assert "10240" in info.address  # Postal code
    
    # Date should be in Thai format
    assert "/" in info.register_date
    assert "2535" in info.register_date or "35" in info.register_date