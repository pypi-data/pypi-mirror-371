from __future__ import annotations

from typing import Optional, Dict, Any
from loguru import logger

from .validators import validate_and_route_tax_id, normalize_branch


class TaxIDRouter:
    """Central routing logic for tax ID lookups with auto-detection.
    
    This class handles:
    - Auto-detection of 10 vs 13 digit tax IDs
    - Input sanitization and cleaning
    - Caching of validation results for performance
    - Building appropriate form data for API requests
    """
    
    def __init__(self, enable_cache: bool = True):
        """Initialize the router.
        
        Args:
            enable_cache: Whether to cache validation results for performance
        """
        self.enable_cache = enable_cache
        self._validation_cache: Dict[str, Any] = {}
        logger.debug(f"TaxIDRouter initialized with cache={'enabled' if enable_cache else 'disabled'}")
    
    def route(self, tax_id: str, branch_no: Optional[str] = None) -> Dict[str, Any]:
        """Route a tax ID to the appropriate validation and form building.
        
        Args:
            tax_id: Tax ID to route (can include spaces, dashes)
            branch_no: Optional branch number
            
        Returns:
            Dictionary with routing information:
                - is_valid: Whether the tax ID is valid
                - tax_id_type: "10" or "13" 
                - cleaned_id: Cleaned tax ID
                - branch_no: Normalized branch number
                - form_data: Form data for API request (if valid)
                - error: Error message (if invalid)
                
        Raises:
            ValueError: If tax ID is invalid
        """
        logger.debug(f"Routing tax_id='{tax_id}' branch_no='{branch_no}'")
        
        # Check cache if enabled
        cache_key = f"{tax_id}:{branch_no}"
        if self.enable_cache and cache_key in self._validation_cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._validation_cache[cache_key]
        
        # Validate and route
        validation = validate_and_route_tax_id(tax_id)
        
        if not validation.is_valid:
            result = {
                "is_valid": False,
                "tax_id_type": None,
                "cleaned_id": validation.cleaned_id,
                "branch_no": None,
                "form_data": None,
                "error": validation.error_message
            }
            logger.warning(f"Validation failed: {validation.error_message}")
            if self.enable_cache:
                self._validation_cache[cache_key] = result
            raise ValueError(validation.error_message)
        
        # Normalize branch
        normalized_branch = normalize_branch(branch_no)
        
        # Build form data based on tax ID type
        form_data = self._build_form_data(
            validation.cleaned_id,
            validation.tax_id_type,
            normalized_branch
        )
        
        result = {
            "is_valid": True,
            "tax_id_type": validation.tax_id_type,
            "cleaned_id": validation.cleaned_id,
            "branch_no": normalized_branch,
            "form_data": form_data,
            "error": None
        }
        
        logger.debug(f"Routing successful: type={validation.tax_id_type}, cleaned={validation.cleaned_id}")
        
        # Cache result if enabled
        if self.enable_cache:
            self._validation_cache[cache_key] = result
        
        return result
    
    def _build_form_data(self, tax_id: str, tax_id_type: str, branch_no: Optional[str]) -> Dict[str, str]:
        """Build form data for API request based on tax ID type.
        
        Args:
            tax_id: Cleaned and validated tax ID
            tax_id_type: "10" or "13"
            branch_no: Normalized branch number
            
        Returns:
            Form data dictionary for API request
        """
        if tax_id_type == "13":
            data = {
                "operation": (
                    "searchByTinBraNo" if (branch_no and branch_no != "0") else "searchByTin"
                ),
                "txtTin": tax_id,
            }
            if branch_no and branch_no != "0":
                data["branotxt"] = branch_no
            logger.debug(f"Built form data for 13-digit: operation={data['operation']}")
            return data
        else:  # tax_id_type == "10"
            data = {
                "operation": (
                    "searchByTinBraNo" if (branch_no and branch_no != "0") else "searchByTin"
                ),
                "txtTin10": tax_id,
            }
            if branch_no and branch_no != "0":
                data["branotxt10"] = branch_no
            logger.debug(f"Built form data for 10-digit: operation={data['operation']}")
            return data
    
    def clear_cache(self):
        """Clear the validation cache."""
        if self._validation_cache:
            size = len(self._validation_cache)
            self._validation_cache.clear()
            logger.debug(f"Cleared {size} cached validation results")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "enabled": self.enable_cache,
            "size": len(self._validation_cache),
            "max_size": 1000  # Could make this configurable
        }


# Global router instance for convenience
_global_router = TaxIDRouter(enable_cache=True)


def route_tax_id(tax_id: str, branch_no: Optional[str] = None) -> Dict[str, Any]:
    """Route a tax ID using the global router instance.
    
    This is a convenience function that uses a global cached router.
    
    Args:
        tax_id: Tax ID to route
        branch_no: Optional branch number
        
    Returns:
        Routing information dictionary
        
    Raises:
        ValueError: If tax ID is invalid
    """
    return _global_router.route(tax_id, branch_no)