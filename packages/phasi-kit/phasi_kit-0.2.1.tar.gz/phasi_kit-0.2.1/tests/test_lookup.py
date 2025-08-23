from __future__ import annotations

import httpx

from phasi_kit import VATInfoClient, get_tax_info, get_tax_infos


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


def make_transport(html: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        content = html.encode("tis-620", errors="ignore")
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html; charset=TIS-620"},
            content=content,
            request=request,
        )

    return httpx.MockTransport(handler)


def test_lookup_single_10_digit():
    client = VATInfoClient(base_url="https://example.invalid", transport=make_transport(HTML_SINGLE))
    info = client.lookup("3031571440", branch_no="0")
    assert info.tax_id == "3031571440"
    assert info.tax_id_type == "10"
    assert info.company_name.startswith("บริษัท เกษรแอสเซท")
    assert info.address and "เพลินจิต" in info.address
    assert info.register_date == "25/02/2553"
    # plural API should also return 1 item
    many = client.lookup_many("3031571440", branch_no="0")
    assert len(many) == 1
    assert many[0].company_name == info.company_name
    # unified API many=True (inject base_url and transport to avoid network)
    u = get_tax_info(
        "3031571440",
        branch_no="0",
        many=True,
        base_url="https://example.invalid",
        transport=make_transport(HTML_SINGLE),
    )
    assert isinstance(u, list) and len(u) == 1


def test_lookup_multi_13_digit():
    client = VATInfoClient(base_url="https://example.invalid", transport=make_transport(HTML_MULTI))
    # First item via single API (first row behavior)
    one = client.lookup("0107555000023")
    assert one.tax_id_type == "13"
    assert one.company_name.startswith("บริษัท ซีพีเอฟ")
    # Plural API should return multiple branches
    rows = client.lookup_many("0107555000023")
    assert len(rows) >= 2
    # HQ should map to branch_no "0"
    assert any(r.branch_no == "0" for r in rows)
    # One branch should be numeric
    assert any(r.branch_no and r.branch_no.isdigit() for r in rows)
    # unified API many=True (inject base_url and transport to avoid network)
    u = get_tax_info(
        "0107555000023",
        many=True,
        base_url="https://example.invalid",
        transport=make_transport(HTML_MULTI),
    )
    assert isinstance(u, list) and len(u) >= 2
