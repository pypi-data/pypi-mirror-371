from importlib.metadata import PackageNotFoundError, version

from .client import VATInfoClient, get_tax_info, get_tax_infos, lookup
from .async_client import AsyncVATInfoClient, lookup_async
from .models import TaxInfo, TaxLookupError, TaxNotFoundError, TaxValidationError
from .result import TaxInfoResult
from .validators import ValidationResult, validate_and_route_tax_id
from .cache import ResponseCache, AsyncResponseCache

__all__ = [
    # New unified API
    "lookup",
    "lookup_async",
    "TaxInfoResult",
    # Async client
    "AsyncVATInfoClient",
    # Legacy API (backward compatibility)
    "VATInfoClient",
    "get_tax_info",
    "get_tax_infos",
    # Models and errors
    "TaxInfo",
    "TaxLookupError",
    "TaxNotFoundError",
    "TaxValidationError",
    # Validation utilities
    "ValidationResult",
    "validate_and_route_tax_id",
    # Cache classes (for advanced users)
    "ResponseCache",
    "AsyncResponseCache",
]

try:  # best-effort during editable installs
    __version__ = version("phasi-kit")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
