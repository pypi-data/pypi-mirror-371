from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
from loguru import logger


@dataclass
class ValidationResult:
    """Result of tax ID validation with detailed information."""
    is_valid: bool
    tax_id_type: Optional[str]  # "10" or "13"
    cleaned_id: str  # Cleaned version of input
    original_id: str  # Original input
    error_message: Optional[str] = None
    

def is_digits(s: str) -> bool:
    return s.isdigit()


def clean_tax_id(tax_id: str) -> str:
    """Clean tax ID by removing common separators and whitespace.
    
    Args:
        tax_id: Raw tax ID input
        
    Returns:
        Cleaned tax ID with only digits
    """
    if not tax_id:
        return ""
    
    # Remove common separators and whitespace
    cleaned = tax_id.strip().replace("-", "").replace(" ", "").replace(".", "")
    logger.debug(f"Cleaned tax ID: '{tax_id}' -> '{cleaned}'")
    return cleaned


def validate_tax_id_13(tax_id: str) -> bool:
    """Validate 13-digit tax ID per RD front-end script.

    Based on `checkNid` logic from docs/tax_api.md (TIS-620 page JS).
    """
    if not is_digits(tax_id) or len(tax_id) != 13:
        logger.debug(f"13-digit validation failed: not 13 digits (got {len(tax_id) if is_digits(tax_id) else 'non-digit chars'})")
        return False

    d = [int(c) for c in tax_id]
    logger.debug(f"13-digit validation: checking {tax_id}")

    digit1, digit2, digit3, digit4 = d[0], d[1], d[2], d[3]
    if digit1 == 0:
        if f"{digit1}{digit2}{digit3}" == "099":
            if f"{digit1}{digit2}{digit3}{digit4}" not in {"0991", "0992", "0993", "0994"}:
                logger.debug(f"13-digit validation failed: invalid 099x prefix ({digit1}{digit2}{digit3}{digit4})")
                return False
    if digit1 == 9:
        logger.debug(f"13-digit validation failed: starts with 9")
        return False

    weights = list(range(13, 1, -1))  # 13..2 (length 12)
    chk_sum = sum(d[i] * weights[i] for i in range(12))
    last_digit = chk_sum % 11
    logger.debug(f"13-digit checksum: sum={chk_sum}, mod11={last_digit}")

    if last_digit in (0, 1):
        expected = 1 if last_digit == 0 else 0
        valid = d[12] == expected
        logger.debug(f"13-digit checksum: expected={expected}, actual={d[12]}, valid={valid}")
        return valid
    else:
        expected = 11 - last_digit
        valid = d[12] == expected
        logger.debug(f"13-digit checksum: expected={expected}, actual={d[12]}, valid={valid}")
        return valid


def validate_tax_id_10(tax_id: str) -> bool:
    """Validate 10-digit tax ID per RD front-end script (checkTin)."""
    if not is_digits(tax_id) or len(tax_id) != 10:
        logger.debug(f"10-digit validation failed: not 10 digits (got {len(tax_id) if is_digits(tax_id) else 'non-digit chars'})")
        return False

    val = int(tax_id)
    logger.debug(f"10-digit validation: checking {tax_id}")
    if val < 1000000000 or val > 8999999999:
        logger.debug(f"10-digit validation failed: out of range (1000000000-8999999999)")
        return False

    d = [int(c) for c in tax_id]
    weights = [3, 1, 3, 1, 3, 1, 3, 1, 3]
    chk_sum = sum(d[i] * weights[i] for i in range(9))
    last_digit = chk_sum % 10
    t10 = d[9] or 10
    if t10 == 0:
        t10 = 10
    valid = last_digit == (10 - t10)
    logger.debug(f"10-digit checksum: sum={chk_sum}, mod10={last_digit}, check_digit={d[9]}, valid={valid}")
    return valid


def validate_and_route_tax_id(tax_id: str) -> ValidationResult:
    """Validate and auto-route tax ID based on length.
    
    This function automatically detects whether the input is a 10 or 13 digit
    tax ID and validates it accordingly. It also cleans the input by removing
    common separators.
    
    Args:
        tax_id: Tax ID to validate (can include spaces, dashes)
        
    Returns:
        ValidationResult with validation status and metadata
    """
    logger.debug(f"Starting validation for tax ID: '{tax_id}'")
    
    if not tax_id:
        logger.debug("Validation failed: empty input")
        return ValidationResult(
            is_valid=False,
            tax_id_type=None,
            cleaned_id="",
            original_id=tax_id or "",
            error_message="Tax ID cannot be empty"
        )
    
    original = str(tax_id)
    cleaned = clean_tax_id(original)
    
    if not is_digits(cleaned):
        logger.debug(f"Validation failed: non-digit characters after cleaning")
        return ValidationResult(
            is_valid=False,
            tax_id_type=None,
            cleaned_id=cleaned,
            original_id=original,
            error_message="Tax ID must contain only digits"
        )
    
    length = len(cleaned)
    logger.debug(f"Detected {length}-digit tax ID")
    
    if length == 10:
        is_valid = validate_tax_id_10(cleaned)
        return ValidationResult(
            is_valid=is_valid,
            tax_id_type="10" if is_valid else None,
            cleaned_id=cleaned,
            original_id=original,
            error_message=None if is_valid else "Invalid 10-digit tax ID checksum"
        )
    elif length == 13:
        is_valid = validate_tax_id_13(cleaned)
        return ValidationResult(
            is_valid=is_valid,
            tax_id_type="13" if is_valid else None,
            cleaned_id=cleaned,
            original_id=original,
            error_message=None if is_valid else "Invalid 13-digit tax ID checksum"
        )
    else:
        logger.debug(f"Validation failed: invalid length {length} (must be 10 or 13)")
        return ValidationResult(
            is_valid=False,
            tax_id_type=None,
            cleaned_id=cleaned,
            original_id=original,
            error_message=f"Tax ID must be 10 or 13 digits (got {length})"
        )


def normalize_branch(branch_no: Optional[str]) -> Optional[str]:
    if branch_no is None:
        return None
    s = str(branch_no).strip()
    if not s:
        return None
    # RD UI allows 0 or empty for HQ, but branch range is 1..99998
    # We keep the original string to post, but validate numeric range if provided.
    try:
        n = int(s)
    except ValueError:
        return None
    if n < 0 or n > 99998:
        return None
    return str(n)

