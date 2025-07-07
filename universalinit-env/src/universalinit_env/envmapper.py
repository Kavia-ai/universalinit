import os
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple


def get_template_path(framework: str) -> Path:
    """Get the path to the environment template file for a given framework."""
    current_dir = Path(__file__).parent
    template_path = current_dir / framework / "env.template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found for framework: {framework}")
    return template_path


def parse_template_file(template_path: Path) -> Tuple[Dict[str, str], List[str]]:
    """
    Parse a template file and extract the mapping from framework-specific to common env vars.
    
    Returns a tuple of:
    - Dictionary mapping framework-specific env vars to common env vars
    - List of wildcard patterns (e.g., ['REACT_APP_*=*'])
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    mapping = {}
    wildcard_patterns = []
    
    with open(template_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                # Split on first '=' to handle values that might contain '='
                parts = line.split('=', 1)
                if len(parts) == 2:
                    framework_var = parts[0].strip()
                    common_var = parts[1].strip()
                    
                    # Check if this is a wildcard pattern
                    if '*' in framework_var or '*' in common_var:
                        wildcard_patterns.append(line)
                    else:
                        mapping[framework_var] = common_var
    
    return mapping, wildcard_patterns


def apply_wildcard_mapping(common_env: Dict[str, str], wildcard_patterns: List[str]) -> Dict[str, str]:
    """
    Apply wildcard patterns to map common environment variables to framework-specific ones.
    
    Args:
        common_env: Dictionary of common environment variables
        wildcard_patterns: List of wildcard patterns from template
    
    Returns:
        Dictionary of additional framework-specific environment variables from wildcard patterns
    """
    framework_env = {}
    
    for pattern in wildcard_patterns:
        if '=' in pattern:
            framework_pattern, common_pattern = pattern.split('=', 1)
            framework_pattern = framework_pattern.strip()
            common_pattern = common_pattern.strip()
            
            # Handle wildcard patterns generically
            if '*' in framework_pattern and '*' in common_pattern:
                # Convert wildcard patterns to regex patterns
                common_regex = common_pattern.replace('*', '(.*)')
                
                for common_var, value in common_env.items():
                    match = re.match(common_regex, common_var)
                    if match and match.groups():
                        # Replace * in framework pattern with the captured group
                        framework_var = framework_pattern.replace('*', match.group(1))
                        framework_env[framework_var] = value
            elif '*' in framework_pattern and common_pattern == '*':
                # Handle prefix patterns like "PREFIX_*=*"
                prefix = framework_pattern.replace('*', '')
                for common_var, value in common_env.items():
                    framework_var = f"{prefix}{common_var}"
                    framework_env[framework_var] = value
            elif framework_pattern == '*' and '*' in common_pattern:
                # Handle suffix patterns like "*=SUFFIX_*"
                suffix = common_pattern.replace('*', '')
                for common_var, value in common_env.items():
                    if common_var.startswith(suffix):
                        framework_var = common_var[len(suffix):]
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
    mapping, wildcard_patterns = parse_template_file(template_path)
    
    # Create reverse mapping: common_var -> framework_var
    reverse_mapping = {v: k for k, v in mapping.items()}
    
    framework_env = {}
    
    # Apply direct mappings
    for common_var, value in common_env.items():
        if common_var in reverse_mapping:
            framework_var = reverse_mapping[common_var]
            framework_env[framework_var] = value
    
    # Apply wildcard mappings
    wildcard_env = apply_wildcard_mapping(common_env, wildcard_patterns)
    framework_env.update(wildcard_env)
    
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
    mapping, wildcard_patterns = parse_template_file(template_path)
    
    common_env = {}
    
    # Apply direct mappings
    for framework_var, value in framework_env.items():
        if framework_var in mapping:
            common_var = mapping[framework_var]
            common_env[common_var] = value
    
    # Apply reverse wildcard mappings
    for pattern in wildcard_patterns:
        if '=' in pattern:
            framework_pattern, common_pattern = pattern.split('=', 1)
            framework_pattern = framework_pattern.strip()
            common_pattern = common_pattern.strip()
            
            # Handle wildcard patterns generically (reverse direction)
            if '*' in framework_pattern and '*' in common_pattern:
                # Convert wildcard patterns to regex patterns
                framework_regex = framework_pattern.replace('*', '(.*)')
                
                for framework_var, value in framework_env.items():
                    match = re.match(framework_regex, framework_var)
                    if match and match.groups():
                        # Replace * in common pattern with the captured group
                        common_var = common_pattern.replace('*', match.group(1))
                        common_env[common_var] = value
            elif '*' in framework_pattern and common_pattern == '*':
                # Handle prefix patterns like "PREFIX_*=*" (reverse)
                prefix = framework_pattern.replace('*', '')
                for framework_var, value in framework_env.items():
                    if framework_var.startswith(prefix):
                        common_var = framework_var[len(prefix):]
                        common_env[common_var] = value
            elif framework_pattern == '*' and '*' in common_pattern:
                # Handle suffix patterns like "*=SUFFIX_*" (reverse)
                suffix = common_pattern.replace('*', '')
                for framework_var, value in framework_env.items():
                    common_var = f"{suffix}{framework_var}"
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
