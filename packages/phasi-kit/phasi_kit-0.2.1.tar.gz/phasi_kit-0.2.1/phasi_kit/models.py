from __future__ import annotations

from dataclasses import dataclass, field
import sys
from typing import Dict, Optional


class TaxLookupError(Exception):
    """Base exception for VAT lookup errors."""


class TaxNotFoundError(TaxLookupError):
    """Raised when a tax ID is valid but no record is found."""


class TaxValidationError(TaxLookupError):
    """Raised when the provided tax ID or branch is invalid."""


# Use dataclass slots only on Python >= 3.10
_DATACLASS_KW = {"slots": True} if sys.version_info >= (3, 10) else {}

@dataclass(**_DATACLASS_KW)
class TaxInfo:
    """Structured VAT info parsed from RD VATINFO.

    Attributes aim to be stable and English-friendly, while `raw_fields`
    preserves the original Thai label-value pairs.
    """

    tax_id: str
    tax_id_type: str  # "10" or "13"
    branch_no: Optional[str] = None

    company_name: Optional[str] = None
    branch_name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    office_name: Optional[str] = None
    register_date: Optional[str] = None
    cancel_date: Optional[str] = None

    raw_html: Optional[str] = None
    raw_fields: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "tax_id": self.tax_id,
            "tax_id_type": self.tax_id_type,
            "branch_no": self.branch_no,
            "company_name": self.company_name,
            "branch_name": self.branch_name,
            "address": self.address,
            "status": self.status,
            "office_name": self.office_name,
            "register_date": self.register_date,
            "cancel_date": self.cancel_date,
        }
