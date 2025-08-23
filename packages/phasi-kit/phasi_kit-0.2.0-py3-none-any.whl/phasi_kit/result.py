from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, Union, overload
from loguru import logger

from .models import TaxInfo


@dataclass
class TaxInfoResult:
    """Smart wrapper for tax lookup results that handles both single and multiple results.
    
    This class provides a unified interface regardless of whether the lookup returned
    one or multiple TaxInfo objects, improving the user experience by not requiring
    upfront knowledge of the result count.
    
    Attributes:
        results: List of TaxInfo objects from the lookup
        query_tax_id: The original tax ID that was queried
        
    Properties:
        is_single: True if only one result was returned
        single: Returns the single TaxInfo if is_single, else raises ValueError
        first: Returns the first TaxInfo result (useful for any case)
        all: Returns all TaxInfo results as a list
        count: Number of results
        
    Examples:
        >>> result = lookup("0107555000023")
        >>> if result.is_single:
        ...     print(result.single.company_name)
        ... else:
        ...     for info in result:
        ...         print(f"Branch {info.branch_no}: {info.company_name}")
        
        >>> # Or simply use first for most common case
        >>> print(result.first.company_name)
        
        >>> # Direct attribute access proxies to first result
        >>> print(result.company_name)  # Same as result.first.company_name
    """
    
    results: list[TaxInfo]
    query_tax_id: str
    
    def __post_init__(self):
        if not self.results:
            logger.warning(f"TaxInfoResult created with empty results for tax_id={self.query_tax_id}")
    
    @property
    def is_single(self) -> bool:
        """Check if this result contains exactly one TaxInfo."""
        return len(self.results) == 1
    
    @property
    def single(self) -> TaxInfo:
        """Get the single TaxInfo result.
        
        Raises:
            ValueError: If results contain zero or more than one TaxInfo
        """
        if not self.results:
            raise ValueError(f"No results found for tax_id={self.query_tax_id}")
        if len(self.results) > 1:
            raise ValueError(
                f"Multiple results ({len(self.results)}) found for tax_id={self.query_tax_id}. "
                "Use .first or .all instead"
            )
        return self.results[0]
    
    @property
    def first(self) -> Optional[TaxInfo]:
        """Get the first TaxInfo result, or None if no results."""
        if not self.results:
            return None
        return self.results[0]
    
    @property
    def all(self) -> list[TaxInfo]:
        """Get all TaxInfo results as a list."""
        return self.results
    
    @property
    def count(self) -> int:
        """Get the number of results."""
        return len(self.results)
    
    def __len__(self) -> int:
        """Support len(result)."""
        return len(self.results)
    
    def __bool__(self) -> bool:
        """Support if result: (True if has results)."""
        return bool(self.results)
    
    def __iter__(self) -> Iterator[TaxInfo]:
        """Support for info in result:"""
        return iter(self.results)
    
    @overload
    def __getitem__(self, index: int) -> TaxInfo: ...
    
    @overload
    def __getitem__(self, index: slice) -> list[TaxInfo]: ...
    
    def __getitem__(self, index: Union[int, slice]) -> Union[TaxInfo, list[TaxInfo]]:
        """Support result[0] or result[0:2]."""
        return self.results[index]
    
    def __getattr__(self, name: str):
        """Proxy attribute access to the first result for convenience.
        
        This allows direct access like result.company_name instead of result.first.company_name
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        first = self.first
        if first is None:
            raise AttributeError(f"No results to proxy attribute '{name}' from")
        
        try:
            return getattr(first, name)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object and its first TaxInfo result "
                f"have no attribute '{name}'"
            )
    
    def filter_by_branch(self, branch_no: Optional[str]) -> list[TaxInfo]:
        """Filter results by branch number.
        
        Args:
            branch_no: Branch number to filter by (None, "0" for HQ, or numeric string)
            
        Returns:
            List of TaxInfo objects matching the branch number
        """
        if branch_no is None:
            return [r for r in self.results if r.branch_no is None]
        
        branch_str = str(branch_no).strip()
        return [r for r in self.results if r.branch_no == branch_str]
    
    def get_branch(self, branch_no: str) -> Optional[TaxInfo]:
        """Get a specific branch by number.
        
        Args:
            branch_no: Branch number ("0" for HQ, or numeric string)
            
        Returns:
            TaxInfo for the branch if found, None otherwise
        """
        matches = self.filter_by_branch(branch_no)
        return matches[0] if matches else None
    
    def has_branch(self, branch_no: str) -> bool:
        """Check if a specific branch exists in results.
        
        Args:
            branch_no: Branch number to check
            
        Returns:
            True if branch exists in results
        """
        return self.get_branch(branch_no) is not None
    
    @property
    def branches(self) -> list[str]:
        """Get list of all branch numbers in results."""
        return [r.branch_no for r in self.results if r.branch_no is not None]
    
    @property
    def hq(self) -> Optional[TaxInfo]:
        """Get the headquarters (branch "0") if present."""
        return self.get_branch("0")
    
    def to_dict(self) -> dict:
        """Convert result to dictionary format."""
        return {
            "query_tax_id": self.query_tax_id,
            "count": self.count,
            "is_single": self.is_single,
            "results": [r.to_dict() for r in self.results]
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.is_single:
            return f"TaxInfoResult(single, tax_id={self.query_tax_id}, company={self.first.company_name})"
        else:
            return f"TaxInfoResult({self.count} results, tax_id={self.query_tax_id}, branches={self.branches})"