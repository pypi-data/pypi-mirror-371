from __future__ import annotations

import pytest
from phasi_kit import TaxInfo, TaxInfoResult


def create_sample_info(tax_id: str, branch_no: str = None, company: str = "Test Co") -> TaxInfo:
    """Helper to create sample TaxInfo objects."""
    return TaxInfo(
        tax_id=tax_id,
        tax_id_type="13" if len(tax_id) == 13 else "10",
        branch_no=branch_no,
        company_name=f"{company} Branch {branch_no or 'HQ'}",
        address="123 Test Street",
        register_date="01/01/2020"
    )


def test_result_single():
    """Test TaxInfoResult with single result."""
    info = create_sample_info("0107555000023", "0")
    result = TaxInfoResult(results=[info], query_tax_id="0107555000023")
    
    assert result.is_single
    assert result.single == info
    assert result.first == info
    assert result.count == 1
    assert len(result) == 1
    assert bool(result) is True
    
    # Test iteration
    items = list(result)
    assert len(items) == 1
    assert items[0] == info
    
    # Test indexing
    assert result[0] == info
    
    # Test attribute proxy
    assert result.company_name == info.company_name
    assert result.address == info.address


def test_result_multiple():
    """Test TaxInfoResult with multiple results."""
    infos = [
        create_sample_info("0107555000023", "0", "CPF"),
        create_sample_info("0107555000023", "1", "CPF"),
        create_sample_info("0107555000023", "2", "CPF"),
    ]
    result = TaxInfoResult(results=infos, query_tax_id="0107555000023")
    
    assert not result.is_single
    assert result.first == infos[0]
    assert result.all == infos
    assert result.count == 3
    assert len(result) == 3
    
    # Test single property raises error
    with pytest.raises(ValueError, match="Multiple results"):
        _ = result.single
    
    # Test iteration
    items = list(result)
    assert items == infos
    
    # Test slicing
    assert result[0:2] == infos[0:2]
    
    # Test attribute proxy (goes to first)
    assert result.company_name == infos[0].company_name


def test_result_empty():
    """Test TaxInfoResult with no results."""
    result = TaxInfoResult(results=[], query_tax_id="0107555000023")
    
    assert not result.is_single
    assert result.first is None
    assert result.all == []
    assert result.count == 0
    assert len(result) == 0
    assert bool(result) is False
    
    # Test single property raises error
    with pytest.raises(ValueError, match="No results"):
        _ = result.single
    
    # Test attribute proxy raises error
    with pytest.raises(AttributeError, match="No results"):
        _ = result.company_name


def test_result_branch_filtering():
    """Test branch filtering methods."""
    infos = [
        create_sample_info("0107555000023", "0"),
        create_sample_info("0107555000023", "1"),
        create_sample_info("0107555000023", "2"),
        create_sample_info("0107555000023", None),
    ]
    result = TaxInfoResult(results=infos, query_tax_id="0107555000023")
    
    # Test filter_by_branch
    hq_only = result.filter_by_branch("0")
    assert len(hq_only) == 1
    assert hq_only[0].branch_no == "0"
    
    branch1 = result.filter_by_branch("1")
    assert len(branch1) == 1
    assert branch1[0].branch_no == "1"
    
    none_branch = result.filter_by_branch(None)
    assert len(none_branch) == 1
    assert none_branch[0].branch_no is None
    
    # Test get_branch
    hq = result.get_branch("0")
    assert hq is not None
    assert hq.branch_no == "0"
    
    missing = result.get_branch("999")
    assert missing is None
    
    # Test has_branch
    assert result.has_branch("0")
    assert result.has_branch("1")
    assert not result.has_branch("999")
    
    # Test branches property
    branches = result.branches
    assert set(branches) == {"0", "1", "2"}  # None is excluded
    
    # Test hq property
    assert result.hq == infos[0]


def test_result_to_dict():
    """Test to_dict conversion."""
    infos = [
        create_sample_info("0107555000023", "0"),
        create_sample_info("0107555000023", "1"),
    ]
    result = TaxInfoResult(results=infos, query_tax_id="0107555000023")
    
    data = result.to_dict()
    assert data["query_tax_id"] == "0107555000023"
    assert data["count"] == 2
    assert data["is_single"] is False
    assert len(data["results"]) == 2
    assert all(isinstance(r, dict) for r in data["results"])


def test_result_repr():
    """Test string representation."""
    # Single result
    info = create_sample_info("0107555000023", "0", "Test Corp")
    result = TaxInfoResult(results=[info], query_tax_id="0107555000023")
    repr_str = repr(result)
    assert "single" in repr_str
    assert "0107555000023" in repr_str
    assert "Test Corp" in repr_str
    
    # Multiple results
    infos = [
        create_sample_info("0107555000023", "0"),
        create_sample_info("0107555000023", "1"),
    ]
    result = TaxInfoResult(results=infos, query_tax_id="0107555000023")
    repr_str = repr(result)
    assert "2 results" in repr_str
    assert "0107555000023" in repr_str
    assert "branches" in repr_str


def test_result_invalid_attribute():
    """Test accessing invalid attributes."""
    info = create_sample_info("0107555000023", "0")
    result = TaxInfoResult(results=[info], query_tax_id="0107555000023")
    
    # Should raise AttributeError for non-existent attributes
    with pytest.raises(AttributeError):
        _ = result.non_existent_attr
    
    # Private attributes should not be proxied
    with pytest.raises(AttributeError):
        _ = result._private_attr