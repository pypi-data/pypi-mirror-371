from __future__ import annotations

from bs4 import BeautifulSoup
from typing import Dict, Tuple, Optional, List
import re


THAI_TO_EN = {
    # Common labels seen on RD VATINFO pages
    "เลขประจำตัวผู้เสียภาษีอากร": "tax_id",
    "เลขประจำตัวผู้เสียภาษี": "tax_id",
    "ชื่อผู้ประกอบการ": "company_name",
    "ชื่อสถานประกอบการ": "branch_name",
    "ชื่อสาขา": "branch_name",
    "เลขที่สาขา": "branch_no",
    "สถานประกอบการ": "status",
    "สถานะ": "status",
    "ที่อยู่สถานประกอบการ": "address",
    "ที่อยู่": "address",
    "วันที่จดทะเบียน": "register_date",
    "วันที่เริ่มต้นจดทะเบียน": "register_date",
    "วันที่สิ้นสุด": "cancel_date",
    "วันที่ยกเลิก": "cancel_date",
    "สำนักงานสรรพากรพื้นที่": "office_name",
}


def _clean_text(s: str) -> str:
    return " ".join(s.replace("\xa0", " ").split()).strip()


def extract_fields(html: str) -> Dict[str, str]:
    """Extract label-value pairs from any tables and definition lists.

    This is heuristic to be resilient to minor markup changes.
    """
    soup = BeautifulSoup(html, "html.parser")
    fields: Dict[str, str] = {}

    # Try table structures: label in one td, value in next td
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])  # some pages use th for labels
            if len(cells) < 2:
                continue
            label = _clean_text(cells[0].get_text(" "))
            value = _clean_text(cells[1].get_text(" "))
            if label and value:
                fields.setdefault(label, value)

    # Try definition lists
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            label = _clean_text(dt.get_text(" "))
            value = _clean_text(dd.get_text(" "))
            if label and value:
                fields.setdefault(label, value)

    # Fallback fuzzy scan: look for known Thai labels anywhere and take nearby text
    def nearest_text_value(node) -> str:
        # Prefer same row second cell if in a table row
        tr = node.find_parent("tr")
        if tr:
            cells = tr.find_all(["td", "th"])
            if len(cells) >= 2:
                return _clean_text(cells[1].get_text(" "))
        # Try next siblings
        sib = node.parent
        if sib:
            # If this node is a label container, use its next sibling text
            nxt = sib.find_next_sibling()
            if nxt:
                return _clean_text(nxt.get_text(" "))
        # Try the node's next element
        nxt = node.find_next()
        if nxt:
            return _clean_text(nxt.get_text(" "))
        return ""

    for th_label in THAI_TO_EN.keys():
        for tag in soup.find_all(string=lambda s: isinstance(s, str) and th_label in _clean_text(s)):
            val = nearest_text_value(tag)
            if th_label not in fields and val:
                fields[th_label] = val

    return fields


def has_no_results(html: str) -> bool:
    """Detect common 'no results' conditions in the RD VATINFO HTML.

    This checks for well-known Thai phrases rendered by the service when
    a tax ID is valid but not a VAT registrant, and other generic phrases.
    """
    lowered = (html or "").lower()
    patterns = [
        "ไม่ใช่ผู้ประกอบการภาษีมูลค่าเพิ่ม",  # not a VAT registrant
        "ไม่พบ",  # not found
        "ไม่มีข้อมูล",  # no data
        "no result",
        "not found",
        "no data",
    ]
    return any(p in lowered for p in patterns)


def _headers_in(row) -> List[str]:
    cells = row.find_all(["th", "td"])
    return [_clean_text(c.get_text(" ")) for c in cells]


def parse_search_results(html: str, query_tax_id: Optional[str] = None) -> Dict[str, str]:
    """Parse the main search results table and return mapped fields.

    The results table typically has headers like:
    - ลำดับ | เลขประจำตัว ผู้เสียภาษีอากร | สาขา | ชื่อผู้ประกอบการ / ชื่อสถานประกอบการ | ที่อยู่ | รหัส ไปรษณีย์ | วันที่ จดทะเบียน | ประวัติการ จดทะเบียน
    """
    soup = BeautifulSoup(html, "html.parser")

    header_keys = {
        "ลำดับ": "index",
        "เลขประจำตัว ผู้เสียภาษีอากร": "tax",
        "เลขประจำตัวผู้เสียภาษีอากร": "tax",
        "สาขา": "branch_col",
        "ชื่อผู้ประกอบการ / ชื่อสถานประกอบการ": "name_col",
        "ชื่อผู้ประกอบการ": "name_col",
        "ชื่อสถานประกอบการ": "name_col",
        "ที่อยู่": "address",
        "ที่อยู่สถานประกอบการ": "address",
        "รหัส ไปรษณีย์": "postal",
        "วันที่ จดทะเบียน": "register_date",
        "วันที่จดทะเบียน": "register_date",
        "ประวัติการ จดทะเบียน": "history",
    }

    def normalize_header(h: str) -> str:
        return h.replace("\u200b", "").replace("\ufeff", "").strip()

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        # Find the header row by content (robust to colspan/rowspan)
        header_row = None
        for r in rows:
            texts = [normalize_header(t) for t in _headers_in(r)]
            joined = " ".join(texts)
            if ("ชื่อผู้ประกอบการ" in joined or "ชื่อสถานประกอบการ" in joined) and (
                "ที่อยู่" in joined
            ):
                header_row = r
                break
        if header_row is None:
            continue

        header_texts = [normalize_header(t) for t in _headers_in(header_row)]
        index_to_key: Dict[int, str] = {}
        for i, h in enumerate(header_texts):
            for th_label, k in header_keys.items():
                if th_label in h:
                    index_to_key[i] = k
                    break
        if len(index_to_key) < 2:  # need at least name and address
            continue

        # The data row should be the next tr with td cells and not a header
        data_cells = None
        found_header = False
        for r in rows:
            if r is header_row:
                found_header = True
                continue
            if not found_header:
                continue
            cells = r.find_all("td")
            if not cells:
                continue
            cell_texts = [normalize_header(c.get_text(" ")) for c in cells]
            # Heuristic: skip rows that still look like headers
            if any("ชื่อผู้ประกอบการ" in t or "ที่อยู่" in t for t in cell_texts):
                continue
            data_cells = cells
            break
        if not data_cells:
            continue

        values_by_key: Dict[str, str] = {}
        for idx, key in index_to_key.items():
            if idx < len(data_cells):
                values_by_key[key] = _clean_text(data_cells[idx].get_text(" "))

        mapped: Dict[str, str] = {}
        name = values_by_key.get("name_col")
        if name:
            mapped["company_name"] = name.split("/")[0].strip()
        branch_name = values_by_key.get("branch_col")
        if branch_name:
            mapped["branch_name"] = branch_name
        addr = values_by_key.get("address")
        if addr:
            postal = values_by_key.get("postal")
            if postal and postal not in addr:
                addr = f"{addr} {postal}".strip()
            mapped["address"] = addr
        reg = values_by_key.get("register_date")
        if reg:
            mapped["register_date"] = reg

        if mapped:
            return mapped

    # Row-based fallback: find a row containing the queried tax id(s)
    if query_tax_id:
        ten = re.compile(r"\b\d{10}\b")
        thirteen = re.compile(r"\b\d{13}\b")
        for table in soup.find_all("table"):
            for r in table.find_all("tr"):
                cells = r.find_all("td")
                if not cells:
                    continue
                row_text = _clean_text(r.get_text(" "))
                if query_tax_id not in row_text:
                    continue
                texts = [_clean_text(c.get_text(" ")) for c in cells]
                # Try to locate the tax-id cell index (contains 10 or 13 digits)
                tax_idx = None
                for i, t in enumerate(texts):
                    if ten.search(t) or thirteen.search(t):
                        tax_idx = i
                        break
                if tax_idx is None:
                    continue
                mapped: Dict[str, str] = {}
                # Heuristic column mapping relative to tax column
                # [tax_idx]  -> tax ids (ignore)
                # [tax_idx+1] -> branch name
                # [tax_idx+2] -> name (may include " / ")
                # [tax_idx+3] -> address
                # [tax_idx+4] -> postal (if 5 digits)
                # [tax_idx+5] -> register date (dd/mm/yyyy)
                if tax_idx + 1 < len(texts):
                    mapped["branch_name"] = texts[tax_idx + 1]
                if tax_idx + 2 < len(texts):
                    name = texts[tax_idx + 2]
                    mapped["company_name"] = name.split("/")[0].strip()
                if tax_idx + 3 < len(texts):
                    addr = texts[tax_idx + 3]
                    # optional postal next
                    if tax_idx + 4 < len(texts) and re.fullmatch(r"\d{5}", texts[tax_idx + 4]):
                        if texts[tax_idx + 4] not in addr:
                            addr = f"{addr} {texts[tax_idx + 4]}"
                    mapped["address"] = addr
                if tax_idx + 5 < len(texts):
                    date = texts[tax_idx + 5]
                    if re.search(r"\d{2}/\d{2}/\d{4}", date):
                        mapped["register_date"] = date
                if mapped:
                    return mapped

    return {}


def parse_search_results_rows(html: str, query_tax_id: Optional[str] = None) -> List[Dict[str, str]]:
    """Parse all result rows into a list of mapped dicts.

    Each dict may contain keys: company_name, branch_name, address, postal,
    register_date. The function is resilient to header variations and falls
    back to column positions relative to the tax-id cell.
    """
    soup = BeautifulSoup(html, "html.parser")

    def normalize_header(h: str) -> str:
        return h.replace("\u200b", "").replace("\ufeff", "").strip()

    header_keys = {
        "ลำดับ": "index",
        "เลขประจำตัว ผู้เสียภาษีอากร": "tax",
        "เลขประจำตัวผู้เสียภาษีอากร": "tax",
        "สาขา": "branch_col",
        "ชื่อผู้ประกอบการ / ชื่อสถานประกอบการ": "name_col",
        "ชื่อผู้ประกอบการ": "name_col",
        "ชื่อสถานประกอบการ": "name_col",
        "ที่อยู่": "address",
        "ที่อยู่สถานประกอบการ": "address",
        "รหัส ไปรษณีย์": "postal",
        "วันที่ จดทะเบียน": "register_date",
        "วันที่จดทะเบียน": "register_date",
        "ประวัติการ จดทะเบียน": "history",
    }

    results: List[Dict[str, str]] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        # Locate header row by presence of well-known labels
        header_row = None
        for r in rows:
            texts = [normalize_header(t) for t in _headers_in(r)]
            joined = " ".join(texts)
            if ("ชื่อผู้ประกอบการ" in joined or "ชื่อสถานประกอบการ" in joined) and (
                "ที่อยู่" in joined
            ):
                header_row = r
                break
        if header_row is None:
            continue

        header_texts = [normalize_header(t) for t in _headers_in(header_row)]
        index_to_key: Dict[int, str] = {}
        for i, h in enumerate(header_texts):
            for th_label, k in header_keys.items():
                if th_label in h:
                    index_to_key[i] = k
                    break
        if len(index_to_key) < 2:
            continue

        # Iterate subsequent data rows
        after_header = False
        for r in rows:
            if r is header_row:
                after_header = True
                continue
            if not after_header:
                continue
            cells = r.find_all("td")
            if not cells:
                continue
            cell_texts = [_clean_text(c.get_text(" ")) for c in cells]
            # Skip rows that still look like a header or are empty
            if not any(cell_texts):
                continue
            if any("ชื่อผู้ประกอบการ" in t or "ที่อยู่" in t for t in cell_texts):
                continue

            values_by_key: Dict[str, str] = {}
            for idx, key in index_to_key.items():
                if idx < len(cells):
                    values_by_key[key] = cell_texts[idx]

            mapped: Dict[str, str] = {}
            name = values_by_key.get("name_col")
            if name:
                mapped["company_name"] = name.split("/")[0].strip()
            branch_name = values_by_key.get("branch_col")
            if branch_name:
                mapped["branch_name"] = branch_name
            addr = values_by_key.get("address")
            if addr:
                postal = values_by_key.get("postal")
                if postal and postal not in addr:
                    addr = f"{addr} {postal}".strip()
                mapped["address"] = addr
            reg = values_by_key.get("register_date")
            if reg:
                mapped["register_date"] = reg

            if mapped:
                results.append(mapped)

        if results:
            return results

    # Fallback: per-row relative mapping based on tax id column
    if query_tax_id:
        ten = re.compile(r"\b\d{10}\b")
        thirteen = re.compile(r"\b\d{13}\b")
        for table in soup.find_all("table"):
            for r in table.find_all("tr"):
                cells = r.find_all("td")
                if not cells:
                    continue
                row_text = _clean_text(r.get_text(" "))
                if query_tax_id not in row_text:
                    continue
                texts = [_clean_text(c.get_text(" ")) for c in cells]
                tax_idx = None
                for i, t in enumerate(texts):
                    if ten.search(t) or thirteen.search(t):
                        tax_idx = i
                        break
                if tax_idx is None:
                    continue
                mapped: Dict[str, str] = {}
                if tax_idx + 1 < len(texts):
                    mapped["branch_name"] = texts[tax_idx + 1]
                if tax_idx + 2 < len(texts):
                    name = texts[tax_idx + 2]
                    mapped["company_name"] = name.split("/")[0].strip()
                if tax_idx + 3 < len(texts):
                    addr = texts[tax_idx + 3]
                    if tax_idx + 4 < len(texts) and re.fullmatch(r"\d{5}", texts[tax_idx + 4]):
                        if texts[tax_idx + 4] not in addr:
                            addr = f"{addr} {texts[tax_idx + 4]}"
                    mapped["address"] = addr
                if tax_idx + 5 < len(texts):
                    date = texts[tax_idx + 5]
                    if re.search(r"\d{2}/\d{2}/\d{4}", date):
                        mapped["register_date"] = date
                if mapped:
                    results.append(mapped)
        if results:
            return results

    return []


def map_fields(fields_th: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Map Thai labels to English keys, return (mapped, raw)."""
    mapped: Dict[str, str] = {}
    for th_label, value in fields_th.items():
        key = None
        for prefix, en in THAI_TO_EN.items():
            if prefix in th_label:
                key = en
                break
        if key:
            # keep first occurrence
            mapped.setdefault(key, value)
    return mapped, dict(fields_th)
