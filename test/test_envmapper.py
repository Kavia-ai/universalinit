import pytest
import tempfile
import os
from pathlib import Path
from universalinit_env.envmapper import (
    get_template_path,
    parse_template_file,
    map_common_to_framework,
    map_framework_to_common,
    get_supported_frameworks,
    apply_wildcard_mapping,
)


class TestTemplatePath:
    """Test template path functionality."""
    
    def test_get_template_path_existing(self):
        """Test getting template path for an existing framework."""
        path = get_template_path("react")
        assert path.exists()
        assert path.name == "env.template"
        assert "react" in str(path)
    
    def test_get_template_path_nonexistent(self):
        """Test getting template path for a nonexistent framework."""
        with pytest.raises(FileNotFoundError):
            get_template_path("nonexistent_framework")


class TestParseTemplateFile:
    """Test template file parsing functionality."""
    
    def test_parse_template_file_existing(self):
        """Test parsing an existing template file."""
        template_path = get_template_path("react")
        mapping, wildcard_patterns = parse_template_file(template_path)
        
        assert isinstance(mapping, dict)
        assert isinstance(wildcard_patterns, list)
        
        # Check direct mappings
        assert "REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT" in mapping
        assert mapping["REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT"] == "SAMPLE_ENV_FOR_UNIINIT"
        
        # Check wildcard patterns
        assert "REACT_APP_*=*" in wildcard_patterns
    
    def test_parse_template_file_nonexistent(self):
        """Test parsing a nonexistent template file."""
        with pytest.raises(FileNotFoundError):
            parse_template_file(Path("nonexistent/path/env.template"))
    
    def test_parse_template_file_with_comments(self):
        """Test parsing template file with comments and empty lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("\n")  # Empty line
            f.write("FRAMEWORK_VAR=COMMON_VAR\n")
            f.write("# Another comment\n")
            f.write("PREFIX_*=*\n")
            f.write("  # Indented comment\n")
            f.write("  SPACED_VAR = SPACED_COMMON_VAR  \n")
        
        try:
            template_path = Path(f.name)
            mapping, wildcard_patterns = parse_template_file(template_path)
            
            assert "FRAMEWORK_VAR" in mapping
            assert mapping["FRAMEWORK_VAR"] == "COMMON_VAR"
            assert "SPACED_VAR" in mapping
            assert mapping["SPACED_VAR"] == "SPACED_COMMON_VAR"
            assert "PREFIX_*=*" in wildcard_patterns
            assert len(wildcard_patterns) == 1
        finally:
            os.unlink(f.name)


class TestWildcardMapping:
    """Test wildcard pattern mapping functionality."""
    
    def test_apply_wildcard_mapping_prefix_pattern(self):
        """Test wildcard mapping with prefix pattern (PREFIX_*=*)."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "DEBUG": "true"
        }
        wildcard_patterns = ["REACT_APP_*=*"]
        
        result = apply_wildcard_mapping(common_env, wildcard_patterns)
        
        assert "REACT_APP_DATABASE_URL" in result
        assert result["REACT_APP_DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "REACT_APP_API_KEY" in result
        assert result["REACT_APP_API_KEY"] == "abc123"
        assert "REACT_APP_DEBUG" in result
        assert result["REACT_APP_DEBUG"] == "true"
    
    def test_apply_wildcard_mapping_complex_pattern(self):
        """Test wildcard mapping with complex pattern (PATTERN_*=*_PATTERN)."""
        common_env = {
            "USER_API_KEY": "secret123",
            "ADMIN_API_KEY": "admin456"
        }
        wildcard_patterns = ["API_*_KEY=*_API_KEY"]
        
        result = apply_wildcard_mapping(common_env, wildcard_patterns)
        
        assert "API_USER_KEY" in result
        assert result["API_USER_KEY"] == "secret123"
        assert "API_ADMIN_KEY" in result
        assert result["API_ADMIN_KEY"] == "admin456"
    
    def test_apply_wildcard_mapping_multiple_patterns(self):
        """Test wildcard mapping with multiple patterns."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123"
        }
        wildcard_patterns = [
            "REACT_APP_*=*",
            "NEXT_PUBLIC_*=*"
        ]
        
        result = apply_wildcard_mapping(common_env, wildcard_patterns)
        
        # Should apply both patterns
        assert "REACT_APP_DATABASE_URL" in result
        assert "REACT_APP_API_KEY" in result
        assert "NEXT_PUBLIC_DATABASE_URL" in result
        assert "NEXT_PUBLIC_API_KEY" in result
    
    def test_apply_wildcard_mapping_no_patterns(self):
        """Test wildcard mapping with no patterns."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb"
        }
        wildcard_patterns = []
        
        result = apply_wildcard_mapping(common_env, wildcard_patterns)
        
        assert result == {}


class TestFrameworkMapping:
    """Test framework-specific mapping functionality."""
    
    def test_map_common_to_framework_react(self):
        """Test mapping common env vars to React framework format."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "DEBUG": "true",
            "SAMPLE_ENV_FOR_UNIINIT": "test_value"
        }
        
        framework_env = map_common_to_framework("react", common_env)
        
        # Check direct mappings
        assert "REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT" in framework_env
        assert framework_env["REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT"] == "test_value"
        
        # Check wildcard mappings
        assert "REACT_APP_DATABASE_URL" in framework_env
        assert framework_env["REACT_APP_DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "REACT_APP_API_KEY" in framework_env
        assert framework_env["REACT_APP_API_KEY"] == "abc123"
        assert "REACT_APP_DEBUG" in framework_env
        assert framework_env["REACT_APP_DEBUG"] == "true"
    
    def test_map_framework_to_common_react(self):
        """Test mapping React framework env vars to common format."""
        framework_env = {
            "REACT_APP_DATABASE_URL": "postgresql://localhost:5432/mydb",
            "REACT_APP_API_KEY": "abc123",
            "REACT_APP_DEBUG": "true",
            "REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT": "test_value",
            "UNKNOWN_VAR": "should-be-ignored"
        }
        
        common_env = map_framework_to_common("react", framework_env)
        
        # Check direct mappings
        assert "SAMPLE_ENV_FOR_UNIINIT" in common_env
        assert common_env["SAMPLE_ENV_FOR_UNIINIT"] == "test_value"
        
        # Check wildcard mappings
        assert "DATABASE_URL" in common_env
        assert common_env["DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "API_KEY" in common_env
        assert common_env["API_KEY"] == "abc123"
        assert "DEBUG" in common_env
        assert common_env["DEBUG"] == "true"
        
        # Check that unknown vars are ignored
        assert "UNKNOWN_VAR" not in common_env
    
    def test_mapping_roundtrip(self):
        """Test that mapping back and forth preserves data integrity."""
        original_common = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "DEBUG": "true",
            "SAMPLE_ENV_FOR_UNIINIT": "test_value"
        }
        
        # Forward mapping
        framework_env = map_common_to_framework("react", original_common)
        
        # Reverse mapping
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify integrity
        assert set(original_common.keys()) == set(back_to_common.keys())
        for key in original_common:
            assert original_common[key] == back_to_common[key]
    
    def test_mapping_with_empty_env(self):
        """Test mapping with empty environment variables."""
        empty_env = {}
        
        # Forward mapping
        framework_env = map_common_to_framework("react", empty_env)
        assert framework_env == {}
        
        # Reverse mapping
        common_env = map_framework_to_common("react", empty_env)
        assert common_env == {}


class TestSupportedFrameworks:
    """Test supported frameworks functionality."""
    
    def test_get_supported_frameworks(self):
        """Test getting list of supported frameworks."""
        frameworks = get_supported_frameworks()
        
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0
        assert "react" in frameworks
        
        # Verify all returned frameworks have template files
        for framework in frameworks:
            template_path = get_template_path(framework)
            assert template_path.exists()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_mapping_with_special_characters(self):
        """Test mapping with environment variables containing special characters."""
        common_env = {
            "DATABASE_URL": "postgresql://user:pass@host:5432/db?sslmode=require",
            "API_KEY": "abc-123_456.789",
            "DEBUG": "true"
        }
        
        framework_env = map_common_to_framework("react", common_env)
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify special characters are preserved
        assert back_to_common["DATABASE_URL"] == "postgresql://user:pass@host:5432/db?sslmode=require"
        assert back_to_common["API_KEY"] == "abc-123_456.789"
    
    def test_mapping_with_unicode(self):
        """Test mapping with unicode characters."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/db",
            "API_KEY": "db",
            "DEBUG": "true"
        }
        
        framework_env = map_common_to_framework("react", common_env)
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify unicode is preserved
        assert back_to_common["DATABASE_URL"] == "postgresql://localhost:5432/db"
        assert back_to_common["API_KEY"] == "db"
    
    def test_mapping_with_very_long_values(self):
        """Test mapping with very long environment variable values."""
        long_value = "x" * 10000
        common_env = {
            "VERY_LONG_VAR": long_value,
            "DATABASE_URL": "postgresql://localhost:5432/mydb"
        }
        
        framework_env = map_common_to_framework("react", common_env)
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify long values are preserved
        assert back_to_common["VERY_LONG_VAR"] == long_value
        assert len(back_to_common["VERY_LONG_VAR"]) == 10000


class TestIntegration:
    """Integration tests for the envmapper module."""
    
    def test_full_workflow(self):
        """Test the complete workflow from template parsing to mapping."""
        # Get template path
        template_path = get_template_path("react")
        
        # Parse template
        mapping, wildcard_patterns = parse_template_file(template_path)
        
        # Verify template structure
        assert isinstance(mapping, dict)
        assert isinstance(wildcard_patterns, list)
        assert len(wildcard_patterns) > 0
        
        # Test with sample data
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "SAMPLE_ENV_FOR_UNIINIT": "test_value"
        }
        
        # Forward mapping
        framework_env = map_common_to_framework("react", common_env)
        
        # Verify results
        assert "REACT_APP_DATABASE_URL" in framework_env
        assert "REACT_APP_API_KEY" in framework_env
        assert "REACT_CUSTOM_PREIFX_SAMPLE_ENV_FOR_UNIINIT" in framework_env
        
        # Reverse mapping
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify roundtrip integrity
        assert set(common_env.keys()) == set(back_to_common.keys())
        for key in common_env:
            assert common_env[key] == back_to_common[key] 