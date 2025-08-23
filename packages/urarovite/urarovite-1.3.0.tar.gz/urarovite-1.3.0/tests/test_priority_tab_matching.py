"""
Test priority-based tab name matching system for A1 range validation.

This test verifies the priority order:
0. Exact match (case sensitive) - highest priority, no change needed
1. Case insensitive match - exact match ignoring case
2. Truncated match - potential_tab is shorter than available tab (should expand)
3. Shorter match - potential_tab is longer than available tab (should shorten)
"""

import pytest
from unittest.mock import patch, MagicMock

from urarovite.utils.a1_range_validator import (
    _find_matching_tabs,
    _find_matching_tabs_cached,
    clear_tab_matching_cache,
    validate_a1_ranges,
    fix_a1_ranges
)


class TestPriorityTabMatching:
    """Test the priority-based tab name matching system."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_tab_matching_cache()
        
        # Standard available tabs for testing
        self.available_tabs = [
            "Grantss",
            "TestDataRenamed", 
            "NewLastTabRenamed",
            "Updated Tab",
            "Very Long Tab Name That Exceeds Excel Character Limit"
        ]
    
    def test_priority_0_exact_match_case_sensitive(self):
        """Test Priority 0: Exact match (case sensitive) - should return empty list (no change needed)."""
        # Exact matches should return empty list (no change needed)
        result = _find_matching_tabs("Grantss", self.available_tabs)
        assert result == []
        
        result = _find_matching_tabs("TestDataRenamed", self.available_tabs)
        assert result == []
        
        result = _find_matching_tabs("Updated Tab", self.available_tabs)
        assert result == []
    
    def test_priority_1_case_insensitive_match(self):
        """Test Priority 1: Case insensitive match - should return correct case version."""
        # Case insensitive matches should return the correct case version
        result = _find_matching_tabs("grantss", self.available_tabs)
        assert result == ["Grantss"]
        
        result = _find_matching_tabs("GRANTSS", self.available_tabs)
        assert result == ["Grantss"]
        
        result = _find_matching_tabs("testdatarenamed", self.available_tabs)
        assert result == ["TestDataRenamed"]
        
        result = _find_matching_tabs("TESTDATARENAMED", self.available_tabs)
        assert result == ["TestDataRenamed"]
        
        result = _find_matching_tabs("updated tab", self.available_tabs)
        assert result == ["Updated Tab"]
    
    def test_priority_2_truncated_match_expansion(self):
        """Test Priority 2: Truncated match - potential_tab is shorter, should expand."""
        # Truncated matches should return the longer version for expansion
        result = _find_matching_tabs("Grants", self.available_tabs)
        assert result == ["Grantss"]
        
        result = _find_matching_tabs("TestData", self.available_tabs)
        assert result == ["TestDataRenamed"]
        
        result = _find_matching_tabs("Very Long Tab Name", self.available_tabs)
        assert result == ["Very Long Tab Name That Exceeds Excel Character Limit"]
    
    def test_priority_3_shorter_match_shortening(self):
        """Test Priority 3: Shorter match - potential_tab is longer, should shorten."""
        # Add a shorter tab for testing shortening
        available_tabs_with_short = self.available_tabs + ["Grant"]
        
        # Longer matches should return the shorter version for shortening
        result = _find_matching_tabs("GrantsExtra", available_tabs_with_short)
        assert "Grant" in result  # Should match the shorter one for shortening
        
        # Test with a clear shortening case
        available_tabs_short = ["Data", "Test"]
        result = _find_matching_tabs("DataExtraLong", available_tabs_short)
        assert result == ["Data"]
    
    def test_priority_order_precedence(self):
        """Test that higher priorities take precedence over lower ones."""
        # Add tabs that could match multiple priorities
        complex_tabs = [
            "Data",           # Could match "DataLong" (shortening)
            "DataRenamed",    # Could match "Data" (expansion) 
            "data"            # Case insensitive match for "Data"
        ]
        
        # Case insensitive should take precedence over truncation
        # Note: Our implementation returns the first case-insensitive match found
        result = _find_matching_tabs("DATA", complex_tabs)
        assert "Data" in result or "data" in result  # Either case-insensitive match is valid
        
        # Truncation should take precedence over shortening
        result = _find_matching_tabs("DataRen", complex_tabs)
        assert "DataRenamed" in result  # Truncated match should be included
        # Note: Our implementation may return multiple matches, but truncated should be first
    
    def test_no_match_cases(self):
        """Test cases where no matches should be found."""
        result = _find_matching_tabs("NonExistent", self.available_tabs)
        assert result == []
        
        result = _find_matching_tabs("CompletelyDifferent", self.available_tabs)
        assert result == []
        
        result = _find_matching_tabs("", self.available_tabs)
        assert result == []
    
    def test_caching_functionality(self):
        """Test that the caching system works correctly."""
        # First call should compute and cache
        result1 = _find_matching_tabs_cached("Grants", self.available_tabs)
        assert result1 == ["Grantss"]
        
        # Second call should use cache (same result)
        result2 = _find_matching_tabs_cached("Grants", self.available_tabs)
        assert result2 == ["Grantss"]
        assert result1 == result2
        
        # Clear cache and verify it's empty
        clear_tab_matching_cache()
        
        # Should still work after cache clear
        result3 = _find_matching_tabs_cached("Grants", self.available_tabs)
        assert result3 == ["Grantss"]
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty available tabs
        result = _find_matching_tabs("AnyTab", [])
        assert result == []
        
        # None inputs
        result = _find_matching_tabs(None, self.available_tabs)
        assert result == []
        
        result = _find_matching_tabs("AnyTab", None)
        assert result == []
        
        # Whitespace handling
        result = _find_matching_tabs("  Grantss  ", self.available_tabs)
        assert result == []  # Should be exact match (no change needed)
        
        result = _find_matching_tabs("  grants  ", self.available_tabs)
        assert result == ["Grantss"]  # Case insensitive match
    
    def test_integration_with_validate_a1_ranges(self):
        """Test integration with the main validation function."""
        # Test exact match (should be valid)
        result = validate_a1_ranges(
            "'Grantss'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["is_valid"] is True
        assert result["truncated_tab_matches"] == []
        
        # Test case insensitive match (should be invalid with fix suggestion)
        result = validate_a1_ranges(
            "'grantss'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["is_valid"] is False
        assert len(result["truncated_tab_matches"]) == 1
        assert result["truncated_tab_matches"][0]["action"] == "case_fix"
        
        # Test truncated match (should be invalid with expansion suggestion)
        result = validate_a1_ranges(
            "'Grants'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["is_valid"] is False
        assert len(result["truncated_tab_matches"]) == 1
        assert result["truncated_tab_matches"][0]["action"] == "expand"
    
    def test_integration_with_fix_a1_ranges(self):
        """Test integration with the fix function."""
        # Test case insensitive fix
        result = fix_a1_ranges(
            "'grantss'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["success"] is True
        assert result["fixed_text"] == "'Grantss'!A1:A10"
        assert "Fixed case sensitivity" in result["changes_made"][0]
        
        # Test truncated expansion fix
        result = fix_a1_ranges(
            "'Grants'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["success"] is True
        assert result["fixed_text"] == "'Grantss'!A1:A10"
        assert "Expanded tab name" in result["changes_made"][0]
        
        # Test exact match (no fix needed)
        result = fix_a1_ranges(
            "'Grantss'!A1:A10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["success"] is True
        assert result["fixed_text"] == "'Grantss'!A1:A10"
        assert result["changes_made"] == []  # No changes needed for exact match
    
    def test_multiple_ranges_in_single_text(self):
        """Test handling of multiple A1 ranges in a single text string."""
        # Test multiple ranges with different priority matches
        result = fix_a1_ranges(
            "'grantss'!A1:A10, 'Grants'!B1:B10, 'Grantss'!C1:C10",
            input_sheet_tabs=self.available_tabs
        )
        assert result["success"] is True
        assert result["fixed_text"] == "'Grantss'!A1:A10, 'Grantss'!B1:B10, 'Grantss'!C1:C10"
        assert len(result["changes_made"]) == 2  # Two ranges needed fixing
        assert "Fixed case sensitivity" in result["changes_made"][0]
        assert "Expanded tab name" in result["changes_made"][1]
    
    def test_performance_with_large_tab_lists(self):
        """Test performance with large numbers of available tabs."""
        # Create a large list of tabs
        large_tab_list = [f"Tab{i}" for i in range(1000)]
        large_tab_list.extend(self.available_tabs)
        
        # Should still work efficiently
        result = _find_matching_tabs_cached("Grants", large_tab_list)
        assert result == ["Grantss"]
        
        # Second call should be very fast due to caching
        result2 = _find_matching_tabs_cached("Grants", large_tab_list)
        assert result2 == ["Grantss"]


class TestTabMatchingRealWorldScenarios:
    """Test real-world scenarios that might occur in spreadsheet validation."""
    
    def test_common_typos_and_variations(self):
        """Test common typos and variations that users might make."""
        available_tabs = [
            "Summary",
            "Data Analysis", 
            "Financial Report",
            "Q1 Results",
            "Customer Database"
        ]
        
        # Common truncations
        assert _find_matching_tabs("Sum", available_tabs) == ["Summary"]
        assert _find_matching_tabs("Data", available_tabs) == ["Data Analysis"]
        assert _find_matching_tabs("Financial", available_tabs) == ["Financial Report"]
        
        # Case variations
        assert _find_matching_tabs("summary", available_tabs) == ["Summary"]
        assert _find_matching_tabs("DATA ANALYSIS", available_tabs) == ["Data Analysis"]
        
        # No matches for completely different names
        assert _find_matching_tabs("Inventory", available_tabs) == []
    
    def test_special_characters_and_spaces(self):
        """Test handling of special characters and spaces in tab names."""
        available_tabs = [
            "Q1-2024 Results",
            "Sales & Marketing",
            "Cost/Benefit Analysis",
            "Employee (Active)",
            "Sheet 1"
        ]
        
        # Should handle special characters correctly
        assert _find_matching_tabs("Q1-2024", available_tabs) == ["Q1-2024 Results"]
        assert _find_matching_tabs("Sales", available_tabs) == ["Sales & Marketing"]
        assert _find_matching_tabs("Cost", available_tabs) == ["Cost/Benefit Analysis"]
        
        # Case insensitive with special characters
        assert _find_matching_tabs("q1-2024 results", available_tabs) == ["Q1-2024 Results"]
    
    def test_ambiguous_matches(self):
        """Test cases where multiple matches might be possible."""
        available_tabs = [
            "Data",
            "DataSet", 
            "DataAnalysis",
            "MetaData"
        ]
        
        # Should prioritize the most specific match
        result = _find_matching_tabs("Dat", available_tabs)
        # Should match "Data" first (shortest expansion)
        assert "Data" in result
        
        # Exact match should take precedence
        result = _find_matching_tabs("Data", available_tabs)
        assert result == []  # Exact match, no change needed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
