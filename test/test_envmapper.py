import pytest
import tempfile
import os
import yaml
from pathlib import Path
from universalinit_env.envmapper import (
    get_template_path,
    parse_template_file,
    map_common_to_framework,
    map_framework_to_common,
    get_supported_frameworks,
    apply_prefix_mapping,
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
        prefix, mapping = parse_template_file(template_path)
        
        assert isinstance(mapping, dict)
        # prefix can be None or a string
        assert prefix is None or isinstance(prefix, str)
        
        # Check that mapping contains expected keys
        assert "REACT_FOO" in mapping
        assert mapping["REACT_FOO"] == "FOO"
        # Check that prefix is set
        assert prefix == "REACT_APP_"
    
    def test_parse_template_file_nonexistent(self):
        """Test parsing a nonexistent template file."""
        with pytest.raises(FileNotFoundError):
            parse_template_file(Path("nonexistent/path/env.template"))
    
    def test_parse_template_file_with_prefix(self):
        """Test parsing template file with prefix."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            yaml_content = {
                'prefix': 'REACT_APP_',
                'mapping': {
                    'REACT_FOO': 'FOO'
                }
            }
            yaml.dump(yaml_content, f)
        
        try:
            template_path = Path(f.name)
            prefix, mapping = parse_template_file(template_path)
            
            assert prefix == "REACT_APP_"
            assert "REACT_FOO" in mapping
            assert mapping["REACT_FOO"] == "FOO"
        finally:
            os.unlink(f.name)
    
    def test_parse_template_file_without_prefix(self):
        """Test parsing template file without prefix."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            yaml_content = {
                'mapping': {
                    'REACT_FOO': 'FOO'
                }
            }
            yaml.dump(yaml_content, f)
        
        try:
            template_path = Path(f.name)
            prefix, mapping = parse_template_file(template_path)
            
            assert prefix is None
            assert "REACT_FOO" in mapping
            assert mapping["REACT_FOO"] == "FOO"
        finally:
            os.unlink(f.name)
    
    def test_parse_template_file_empty(self):
        """Test parsing empty template file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("")
        
        try:
            template_path = Path(f.name)
            prefix, mapping = parse_template_file(template_path)
            
            assert prefix is None
            assert mapping == {}
        finally:
            os.unlink(f.name)
    
    def test_parse_template_file_invalid_yaml(self):
        """Test parsing invalid YAML template file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("invalid: yaml: content: [")
        
        try:
            template_path = Path(f.name)
            with pytest.raises(ValueError, match="Invalid YAML"):
                parse_template_file(template_path)
        finally:
            os.unlink(f.name)
    
    def test_parse_template_file_invalid_mapping(self):
        """Test parsing template file with invalid mapping type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            yaml_content = {
                'mapping': "not a dict"
            }
            yaml.dump(yaml_content, f)
        
        try:
            template_path = Path(f.name)
            with pytest.raises(ValueError, match="'mapping' must be a dictionary"):
                parse_template_file(template_path)
        finally:
            os.unlink(f.name)


class TestPrefixMapping:
    """Test prefix mapping functionality."""
    
    def test_apply_prefix_mapping(self):
        """Test applying prefix to environment variables."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "DEBUG": "true"
        }
        prefix = "REACT_APP_"
        
        result = apply_prefix_mapping(common_env, prefix)
        
        assert "REACT_APP_DATABASE_URL" in result
        assert result["REACT_APP_DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "REACT_APP_API_KEY" in result
        assert result["REACT_APP_API_KEY"] == "abc123"
        assert "REACT_APP_DEBUG" in result
        assert result["REACT_APP_DEBUG"] == "true"
    
    def test_apply_prefix_mapping_empty(self):
        """Test applying prefix to empty environment."""
        common_env = {}
        prefix = "REACT_APP_"
        
        result = apply_prefix_mapping(common_env, prefix)
        
        assert result == {}


class TestFrameworkMapping:
    """Test framework-specific mapping functionality."""
    
    def test_map_common_to_framework_react(self):
        """Test mapping common env vars to React framework format."""
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "DEBUG": "true",
            "FOO": "bar",
            "UNMAPPED_VAR": "should-be-preserved"
        }
        
        framework_env = map_common_to_framework("react", common_env)
        
        # Check direct mappings
        assert "REACT_FOO" in framework_env
        assert framework_env["REACT_FOO"] == "bar"
        # Check prefix mappings
        assert "REACT_APP_DATABASE_URL" in framework_env
        assert framework_env["REACT_APP_DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "REACT_APP_API_KEY" in framework_env
        assert framework_env["REACT_APP_API_KEY"] == "abc123"
        assert "REACT_APP_DEBUG" in framework_env
        assert framework_env["REACT_APP_DEBUG"] == "true"
        
        # Check that unmapped variables get prefix applied
        assert "REACT_APP_UNMAPPED_VAR" in framework_env
        assert framework_env["REACT_APP_UNMAPPED_VAR"] == "should-be-preserved"
    
    def test_map_framework_to_common_react(self):
        """Test mapping React framework env vars to common format."""
        framework_env = {
            "REACT_FOO": "bar",
            "REACT_APP_DATABASE_URL": "postgresql://localhost:5432/mydb",
            "REACT_APP_API_KEY": "abc123",
            "REACT_APP_DEBUG": "true",
            "UNKNOWN_VAR": "should-be-preserved"
        }
        
        common_env = map_framework_to_common("react", framework_env)
        
        # Check direct mappings
        assert "FOO" in common_env
        assert common_env["FOO"] == "bar"
        # Check prefix mappings
        assert "DATABASE_URL" in common_env
        assert common_env["DATABASE_URL"] == "postgresql://localhost:5432/mydb"
        assert "API_KEY" in common_env
        assert common_env["API_KEY"] == "abc123"
        assert "DEBUG" in common_env
        assert common_env["DEBUG"] == "true"
        
        # Check that unknown vars are preserved
        assert "UNKNOWN_VAR" in common_env
        assert common_env["UNKNOWN_VAR"] == "should-be-preserved"
    
    def test_mapping_roundtrip(self):
        """Test that mapping back and forth preserves data integrity."""
        original_common = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "FOO": "bar"
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


class TestUnmappedVariablePreservation:
    """Test that unmapped environment variables are preserved."""
    
    def test_preserve_unmapped_common_variables(self):
        """Test that common variables without mappings are preserved when mapping to framework."""
        common_env = {
            "FOO": "bar",  # Has direct mapping
            "UNMAPPED_VAR1": "value1",  # No mapping
            "UNMAPPED_VAR2": "value2",  # No mapping
        }
        
        framework_env = map_common_to_framework("react", common_env)
        
        # Check that mapped variables are transformed
        assert "REACT_FOO" in framework_env
        assert framework_env["REACT_FOO"] == "bar"
        
        # Check that unmapped variables get prefix applied
        assert "REACT_APP_UNMAPPED_VAR1" in framework_env
        assert framework_env["REACT_APP_UNMAPPED_VAR1"] == "value1"
        assert "REACT_APP_UNMAPPED_VAR2" in framework_env
        assert framework_env["REACT_APP_UNMAPPED_VAR2"] == "value2"
    
    def test_preserve_unmapped_framework_variables(self):
        """Test that framework variables without mappings are preserved when mapping to common."""
        framework_env = {
            "REACT_FOO": "bar",  # Has direct mapping
            "UNMAPPED_FRAMEWORK_VAR1": "fw_value1",  # No mapping
            "UNMAPPED_FRAMEWORK_VAR2": "fw_value2",  # No mapping
        }
        
        common_env = map_framework_to_common("react", framework_env)
        
        # Check that mapped variables are transformed
        assert "FOO" in common_env
        assert common_env["FOO"] == "bar"
        
        # Check that unmapped variables are preserved as-is
        assert "UNMAPPED_FRAMEWORK_VAR1" in common_env
        assert common_env["UNMAPPED_FRAMEWORK_VAR1"] == "fw_value1"
        assert "UNMAPPED_FRAMEWORK_VAR2" in common_env
        assert common_env["UNMAPPED_FRAMEWORK_VAR2"] == "fw_value2"


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
        prefix, mapping = parse_template_file(template_path)
        
        # Verify template structure
        assert isinstance(mapping, dict)
        assert len(mapping) > 0
        
        # Test with sample data
        common_env = {
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "abc123",
            "FOO": "bar"
        }
        
        # Forward mapping
        framework_env = map_common_to_framework("react", common_env)
        
        # Verify results
        assert "REACT_FOO" in framework_env
        assert framework_env["REACT_FOO"] == "bar"
        
        # Reverse mapping
        back_to_common = map_framework_to_common("react", framework_env)
        
        # Verify roundtrip integrity
        assert set(common_env.keys()) == set(back_to_common.keys())
        for key in common_env:
            assert common_env[key] == back_to_common[key] 