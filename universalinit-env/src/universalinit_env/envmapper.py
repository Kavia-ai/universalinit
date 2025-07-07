import os
from pathlib import Path
from typing import Dict, Optional


def get_template_path(framework: str) -> Path:
    """Get the path to the environment template file for a given framework."""
    current_dir = Path(__file__).parent
    template_path = current_dir / framework / "env.template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found for framework: {framework}")
    return template_path


def parse_template_file(template_path: Path) -> Dict[str, str]:
    """
    Parse a template file and extract the mapping from framework-specific to common env vars.
    
    Returns a dictionary mapping framework-specific env vars to common env vars.
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    mapping = {}
    with open(template_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                # Split on first '=' to handle values that might contain '='
                parts = line.split('=', 1)
                if len(parts) == 2:
                    framework_var = parts[0].strip()
                    common_var = parts[1].strip()
                    mapping[framework_var] = common_var
    
    return mapping


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
    mapping = parse_template_file(template_path)
    
    # Create reverse mapping: common_var -> framework_var
    reverse_mapping = {v: k for k, v in mapping.items()}
    
    framework_env = {}
    for common_var, value in common_env.items():
        if common_var in reverse_mapping:
            framework_var = reverse_mapping[common_var]
            framework_env[framework_var] = value
    
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
    mapping = parse_template_file(template_path)
    
    common_env = {}
    for framework_var, value in framework_env.items():
        if framework_var in mapping:
            common_var = mapping[framework_var]
            common_env[common_var] = value
    
    return common_env


def get_supported_frameworks() -> list:
    """Get a list of supported frameworks based on available template directories."""
    current_dir = Path(__file__).parent
    frameworks = []
    
    for item in current_dir.iterdir():
        if item.is_dir() and (item / "env.template").exists():
            frameworks.append(item.name)
    
    return frameworks
