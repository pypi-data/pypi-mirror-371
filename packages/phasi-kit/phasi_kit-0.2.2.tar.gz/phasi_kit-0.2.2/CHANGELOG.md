# Changelog

All notable changes to phasi-kit will be documented in this file.

## [0.2.2] - 2025-08-23

### Added
- **Response caching support** (disabled by default)
  - Configurable TTL (default 5 minutes)
  - Separate caches for sync and async clients
  - Cache statistics and management methods
  - `enable_cache` and `cache_ttl` parameters

### Changed
- Performance improvement: Skip redundant API calls for repeated lookups when cache is enabled

## [0.2.1] - 2025-08-23

### Changed
- Removed unnecessary `notebook` dependency (not used in the package)

### Fixed
- GitHub Actions publish workflow now properly sets up `uv` for fallback publishing

## [0.2.0] - 2025-08-23

### Added
- **Smart Unified API** with `lookup()` and `lookup_async()` functions
- **Auto-routing** - Automatically detects 10 vs 13 digit tax IDs
- **Input cleaning** - Handles spaces, dashes, dots in tax IDs
- **Full async support** with `AsyncVATInfoClient`
- **Connection pooling** for better performance
- **Request coalescing** - Deduplicates concurrent identical requests
- **Smart result wrapper** `TaxInfoResult` that handles single/multi results intelligently
- Enhanced validation with detailed error messages
- Comprehensive loguru debug logging
- New test suite including async tests and real response tests

### Changed
- Minimum Python version lowered to 3.10 (from 3.12)
- Enhanced `VATInfoClient` with connection pooling
- Improved error messages and validation

### Backward Compatibility
- All existing APIs (`get_tax_info`, `get_tax_infos`) remain unchanged
- Legacy methods still available on `VATInfoClient`

## [0.1.0] - 2025-08-22

### Initial Release
- Basic VAT tax ID lookup for Thai Revenue Department
- Support for 10 and 13 digit tax IDs
- TIS-620 HTML parsing
- Basic retry logic and error handling
- Loguru logging integration