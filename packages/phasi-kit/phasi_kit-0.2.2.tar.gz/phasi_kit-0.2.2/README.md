<p align="center">
  <img src="banner.svg" alt="phasi-kit banner" width="100%">
</p>
<p align="center">
  <em>Thai VAT tax ID lookup for the RD VATINFO service — smart, fast, async-ready</em>
</p>
<p align="center">
<a href="https://github.com/RThaweewat/phasi-kit/actions?query=workflow%3ACI+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/RThaweewat/phasi-kit/actions/workflows/test.yml/badge.svg?event=push&branch=main" alt="CI">
</a>
<a href="https://pypi.org/project/phasi-kit/" target="_blank">
    <img src="https://img.shields.io/pypi/v/phasi-kit?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<img src="https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white" alt="Python >= 3.10">
<a href="https://github.com/RThaweewat/phasi-kit/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/RThaweewat/phasi-kit" alt="License: Apache-2.0">
</a>
</p>

---

**Source Code**: <a href="https://github.com/RThaweewat/phasi-kit" target="_blank">https://github.com/RThaweewat/phasi-kit</a>

**PyPI**: <a href="https://pypi.org/project/phasi-kit/" target="_blank">https://pypi.org/project/phasi-kit/</a>

---

phasi-kit provides a simple, production-friendly client to query Thailand's Revenue Department VATINFO service. It auto-detects 10/13‑digit tax IDs, returns structured results, and supports high-performance async lookups.

## Key Features

* **Unified API**: One `lookup()` for 10/13‑digit IDs; smart multi-branch handling.
* **Async-ready**: `lookup_async()` plus an async client with pooling.
* **Response caching**: Optional caching with TTL to reduce API calls (disabled by default).
* **Robust**: Retries with backoff, request coalescing, and clear errors.
* **Clean parsing**: Converts TIS‑620 HTML into typed `TaxInfo` objects.
* **Ergonomic results**: `result.first`, `result.count`, iterate branches, `result.hq`.

## Requirements

* Python 3.10+

## Installation

```bash
pip install phasi-kit
```

Using uv:

```bash
uv pip install phasi-kit
```

## Example

Create a simple lookup:

```python
from phasi_kit import lookup

result = lookup("0107555000023")  # dashes/spaces also work

print(result.company_name)
print(result.count)
print(result.first.address)
```

```text
# Output:
# บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# 10
# อาคาร ซี.พี.ทาวเวอร์ เลขที่ 313 ถนน สีลม ตำบล/แขวง สีลม อำเภอ/เขต บางรัก จังหวัด กรุงเทพมหานคร 10500
```

Multiple branches:

```python
result = lookup("0107555000023")  # CPF has many branches

# Iterate through branches
for info in result[:5]:  # Show first 5
    print(f"Branch {info.branch_no}: {info.company_name}")
```

```text
# Output:
# Branch 0: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# Branch 00001: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# Branch 00002: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# Branch 00003: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# Branch 00004: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
```

Async lookup:

```python
import asyncio
from phasi_kit import lookup_async

async def main():
    res = await lookup_async("0105534038143")
    print(res.first.company_name)

asyncio.run(main())
```

```text
# Output:
# บริษัท พร็อสเพอร์สโตน จำกัด
```

Lookup with branch:

```python
# Query specific branch
result = lookup("0107555000023", branch_no="00001")
print(f"Branch: {result.first.branch_no}")
print(f"Company: {result.first.company_name}")
print(f"Address: {result.first.address}")
```

```text
# Output:
# Branch: 00001
# Company: บริษัท ซีพีเอฟ (ประเทศไทย) จำกัด (มหาชน)
# Address: เลขที่ 178 หมู่ที่ 4 ถนน พิษณุโลก-หล่มสัก ตำบล/แขวง สมอแข อำเภอ/เขต เมืองพิษณุโลก จังหวัด พิษณุโลก 65000
```

Validation helper:

```python
from phasi_kit import validate_and_route_tax_id

v = validate_and_route_tax_id("0107-555-000023")
print(v.is_valid, v.tax_id_type, v.cleaned_id)
```

```text
# Output:
# True 13 0107555000023
```

## Caching

Response caching to reduce API calls (disabled by default):

```python
# Enable with default 5-minute TTL
result = lookup("0107555000023", enable_cache=True)

# Custom TTL (10 minutes)
client = VATInfoClient(enable_cache=True, cache_ttl=600)
result1 = client.lookup_smart("0107555000023")
result2 = client.lookup_smart("0107555000023")  # Uses cache

# Check cache stats
print(client.get_cache_stats())
# {'size': 1, 'hits': 1, 'misses': 1, 'hit_rate': '50.0%'}

# Clear cache if needed
client.clear_cache()
```

## Environment

* `PHASI_VATINFO_URL`: Override the default RD endpoint if needed.

## License

Apache-2.0 (see `LICENSE`)
