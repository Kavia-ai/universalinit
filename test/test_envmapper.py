import pytest
from pathlib import Path
from universalinit_env import (
    get_template_path,
    parse_template_file,
    map_common_to_framework,
    map_framework_to_common,
    get_supported_frameworks,
)


def test_get_template_path():
    """Test getting template path for a framework."""
    path = get_template_path("react")
    assert path.exists()
    assert path.name == "env.template"
    assert "react" in str(path)


def test_parse_template_file():
    """Test parsing a template file."""
    template_path = get_template_path("react")
    mapping = parse_template_file(template_path)
    
    assert isinstance(mapping, dict)
    assert "REACT_APP_SUPABASE_URL" in mapping
    assert mapping["REACT_APP_SUPABASE_URL"] == "SUPABASE_URL"
    assert mapping["REACT_APP_API_KEY"] == "API_SECRET_KEY"
    assert mapping["REACT_APP_DATABASE_URL"] == "DATABASE_URL"


def test_map_framework_to_common():
    """Test mapping framework-specific env vars to common format."""
    framework_env = {
        "REACT_APP_SUPABASE_URL": "https://example.supabase.co",
        "REACT_APP_API_KEY": "secret-key",
        "REACT_APP_DATABASE_URL": "postgresql://...",
        "UNKNOWN_VAR": "should-be-ignored"
    }
    
    common_env = map_framework_to_common("react", framework_env)
    
    assert "SUPABASE_URL" in common_env
    assert common_env["SUPABASE_URL"] == "https://example.supabase.co"
    assert common_env["API_SECRET_KEY"] == "secret-key"
    assert common_env["DATABASE_URL"] == "postgresql://..."
    assert "UNKNOWN_VAR" not in common_env


def test_map_common_to_framework():
    """Test mapping common env vars to framework-specific format."""
    common_env = {
        "SUPABASE_URL": "https://example.supabase.co",
        "API_SECRET_KEY": "secret-key",
        "DATABASE_URL": "postgresql://...",
        "UNKNOWN_VAR": "should-be-ignored"
    }
    
    framework_env = map_common_to_framework("react", common_env)
    
    assert "REACT_APP_SUPABASE_URL" in framework_env
    assert framework_env["REACT_APP_SUPABASE_URL"] == "https://example.supabase.co"
    assert framework_env["REACT_APP_API_KEY"] == "secret-key"
    assert framework_env["REACT_APP_DATABASE_URL"] == "postgresql://..."
    assert "UNKNOWN_VAR" not in framework_env


def test_get_supported_frameworks():
    """Test getting list of supported frameworks."""
    frameworks = get_supported_frameworks()
    
    assert isinstance(frameworks, list)
    assert "react" in frameworks


def test_nonexistent_framework():
    """Test handling of nonexistent framework."""
    with pytest.raises(FileNotFoundError):
        get_template_path("nonexistent")


def test_parse_nonexistent_template():
    """Test parsing nonexistent template file."""
    with pytest.raises(FileNotFoundError):
        parse_template_file(Path("nonexistent/path/env.template")) 