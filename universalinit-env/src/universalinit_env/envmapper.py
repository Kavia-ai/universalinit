import os
import re
import yaml
from pathlib import Path
from typing import Dict, Optional, List, Tuple


def get_template_path(framework: str) -> Path:
    """Get the path to the environment template file for a given framework."""
    current_dir = Path(__file__).parent
    template_path = current_dir / framework / "env.template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found for framework: {framework}")
    return template_path


def parse_template_file(template_path: Path) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Parse a YAML template file and extract the prefix and mapping.
    
    Returns a tuple of:
    - Optional prefix string (None if not specified)
    - Dictionary mapping framework-specific env vars to common env vars
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in template file: {e}")
    
    if not config:
        return None, {}
    
    # Extract prefix (optional)
    prefix = config.get('prefix')
    
    # Extract mapping
    mapping = config.get('mapping', {})
    if not isinstance(mapping, dict):
        raise ValueError("'mapping' must be a dictionary in the template file")
    
    return prefix, mapping


def apply_prefix_mapping(common_env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """
    Apply prefix to all environment variables.
    
    Args:
        common_env: Dictionary of common environment variables
        prefix: Prefix to add to all variables
    
    Returns:
        Dictionary of framework-specific environment variables with prefix
    """
    framework_env = {}
    for common_var, value in common_env.items():
        framework_var = f"{prefix}{common_var}"
        framework_env[framework_var] = value
    
    return framework_env


def map_common_to_framework(framework: str, common_env: Dict[str, str]) -> Dict[str, str]:
    """
    Map common environment variables to framework-specific ones.
    
    Args:
        framework: The framework name (e.g., 'react')
        common_env: Dictionary of common environment variables
    
    Returns:
        Dictionary of framework-specific environment variables
    """
    template_path = get_template_path(framework)
    prefix, mapping = parse_template_file(template_path)
    
    # Create reverse mapping: common_var -> framework_var
    reverse_mapping = {v: k for k, v in mapping.items()}
    
    framework_env = {}
    mapped_common_vars = set()
    
    # Apply direct mappings first
    for common_var, value in common_env.items():
        if common_var in reverse_mapping:
            framework_var = reverse_mapping[common_var]
            framework_env[framework_var] = value
            mapped_common_vars.add(common_var)
    
    # Apply prefix to unmapped variables if prefix is specified
    if prefix:
        for common_var, value in common_env.items():
            if common_var not in mapped_common_vars:
                framework_var = f"{prefix}{common_var}"
                framework_env[framework_var] = value
                mapped_common_vars.add(common_var)
    
    # Add remaining unmapped variables as-is
    for common_var, value in common_env.items():
        if common_var not in mapped_common_vars:
            framework_env[common_var] = value
    
    return framework_env


def map_framework_to_common(framework: str, framework_env: Dict[str, str]) -> Dict[str, str]:
    """
    Map framework-specific environment variables to common ones.
    
    Args:
        framework: The framework name (e.g., 'react')
        framework_env: Dictionary of framework-specific environment variables
    
    Returns:
        Dictionary of common environment variables
    """
    template_path = get_template_path(framework)
    prefix, mapping = parse_template_file(template_path)
    
    common_env = {}
    mapped_framework_vars = set()
    
    # Apply direct mappings first
    for framework_var, value in framework_env.items():
        if framework_var in mapping:
            common_var = mapping[framework_var]
            common_env[common_var] = value
            mapped_framework_vars.add(framework_var)
    
    # Apply reverse prefix mapping if prefix is specified
    if prefix:
        for framework_var, value in framework_env.items():
            if framework_var not in mapped_framework_vars and framework_var.startswith(prefix):
                common_var = framework_var[len(prefix):]
                common_env[common_var] = value
                mapped_framework_vars.add(framework_var)
    
    # Add remaining unmapped framework variables as-is
    for framework_var, value in framework_env.items():
        if framework_var not in mapped_framework_vars:
            common_env[framework_var] = value
    
    return common_env


def get_supported_frameworks() -> list:
    """Get a list of supported frameworks based on available template directories."""
    current_dir = Path(__file__).parent
    frameworks = []
    
    for item in current_dir.iterdir():
        if item.is_dir() and (item / "env.template").exists():
            frameworks.append(item.name)
    
    return frameworks
