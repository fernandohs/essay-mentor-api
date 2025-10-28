"""
Tests for utils/criteria.py
"""
import pytest
from app.utils.criteria import (
    get_criteria_list,
    get_criterion_info,
    validate_criterion,
    add_criterion,
    validate_all_criteria,
    get_default_criteria_description,
    get_default_criteria_summary
)
from app.models.criterion import CriterionDefinition


class TestGetCriteriaList:
    """Tests for get_criteria_list function."""

    def test_get_criteria_list_returns_list(self):
        """Test that function returns a list."""
        result = get_criteria_list()
        
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_criteria_list_contains_expected_keys(self):
        """Test that list contains expected criteria."""
        result = get_criteria_list()
        
        assert "originalidad" in result
        assert "profundidad" in result
        assert "logica" in result


class TestGetCriterionInfo:
    """Tests for get_criterion_info function."""

    def test_get_criterion_info_existing(self):
        """Test retrieving info for existing criterion."""
        result = get_criterion_info("originalidad")
        
        assert "maxPoints" in result
        assert "description" in result
        assert result["maxPoints"] == 22

    def test_get_criterion_info_nonexistent(self):
        """Test retrieving info for non-existent criterion."""
        result = get_criterion_info("nonexistent")
        
        assert result == {}


class TestValidateCriterion:
    """Tests for validate_criterion function."""

    def test_validate_criterion_success(self):
        """Test successful criterion validation."""
        result = validate_criterion(
            "test_criterion",
            maxPoints=10,
            description="Test description"
        )
        
        assert isinstance(result, CriterionDefinition)
        assert result.maxPoints == 10
        assert result.description == "Test description"

    def test_validate_criterion_zero_points_error(self):
        """Test validation with zero maxPoints."""
        with pytest.raises(ValueError):
            validate_criterion(
                "test",
                maxPoints=0,
                description="Test"
            )

    def test_validate_criterion_negative_points_error(self):
        """Test validation with negative maxPoints."""
        with pytest.raises(ValueError):
            validate_criterion(
                "test",
                maxPoints=-5,
                description="Test"
            )

    def test_validate_criterion_empty_description_error(self):
        """Test validation with empty description."""
        with pytest.raises(ValueError):
            validate_criterion(
                "test",
                maxPoints=10,
                description=""
            )


class TestAddCriterion:
    """Tests for add_criterion function."""

    def test_add_criterion_success(self):
        """Test successfully adding a new criterion."""
        try:
            add_criterion(
                "test_criterion_new",
                maxPoints=5,
                description="New test criterion"
            )
            
            info = get_criterion_info("test_criterion_new")
            assert info["maxPoints"] == 5
            assert info["description"] == "New test criterion"
        finally:
            # Cleanup - remove the test criterion
            from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA
            if "test_criterion_new" in ESSAY_RUBRIC_CRITERIA:
                del ESSAY_RUBRIC_CRITERIA["test_criterion_new"]

    def test_add_criterion_duplicate_error(self):
        """Test error when adding duplicate criterion."""
        with pytest.raises(ValueError) as exc_info:
            add_criterion(
                "originalidad",
                maxPoints=20,
                description="Duplicate"
            )
        
        assert "already exists" in str(exc_info.value)


class TestValidateAllCriteria:
    """Tests for validate_all_criteria function."""

    def test_validate_all_criteria_success(self):
        """Test successful validation of all criteria."""
        result = validate_all_criteria()
        
        assert result is True

    def test_validate_all_criteria_with_invalid(self):
        """Test validation fails with invalid criterion."""
        from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA
        
        # Temporarily corrupt data
        original = ESSAY_RUBRIC_CRITERIA.get("logica", {}).get("maxPoints")
        ESSAY_RUBRIC_CRITERIA["logica"]["maxPoints"] = -1
        
        try:
            with pytest.raises(ValueError):
                validate_all_criteria()
        finally:
            # Restore original value
            if original is not None:
                ESSAY_RUBRIC_CRITERIA["logica"]["maxPoints"] = original


class TestGetDefaultCriteriaDescription:
    """Tests for get_default_criteria_description function."""

    def test_get_default_criteria_description_returns_string(self):
        """Test that function returns a string."""
        result = get_default_criteria_description()
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_default_criteria_description_contains_keys(self):
        """Test that description contains criterion names."""
        result = get_default_criteria_description()
        
        assert "originalidad" in result.lower()
        assert "pts" in result or "pts" in result


class TestGetDefaultCriteriaSummary:
    """Tests for get_default_criteria_summary function."""

    def test_get_default_criteria_summary_returns_string(self):
        """Test that function returns a string."""
        result = get_default_criteria_summary()
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_default_criteria_summary_multiline(self):
        """Test that summary contains multiple lines."""
        result = get_default_criteria_summary()
        
        lines = result.split('\n')
        assert len(lines) > 1

    def test_get_default_criteria_summary_contains_points(self):
        """Test that summary contains point values."""
        result = get_default_criteria_summary()
        
        assert "pts" in result or "pts" in result

