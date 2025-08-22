"""
CSS generation utilities for Django Spellbook's theme system.
"""

from typing import Dict, Optional, Any
from .core import SpellbookTheme


def generate_css_variables(theme_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate CSS variable declarations from a theme configuration.
    
    Args:
        theme_config: Theme configuration dictionary from Django settings
        
    Returns:
        CSS string containing variable declarations
    """
    # Create theme instance
    theme = SpellbookTheme(theme_config)
    
    # Get all CSS declarations
    declarations = theme.to_css_declarations()
    
    # Add border-radius variables (non-color styling variables)
    border_radius_vars = {
        '--sb-border-radius-sm': '0.125rem',
        '--sb-border-radius-md': '0.375rem',
        '--sb-border-radius-lg': '0.5rem',
        '--sb-border-radius-xl': '0.75rem',
        '--sb-border-radius-2xl': '1rem',
    }
    declarations.update(border_radius_vars)
    
    # Build CSS string
    css_lines = [':root {']
    
    # Sort declarations for consistent output
    for var_name in sorted(declarations.keys()):
        value = declarations[var_name]
        css_lines.append(f'  {var_name}: {value};')
    
    css_lines.append('}')
    
    return '\n'.join(css_lines)


def generate_theme_css(theme_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate complete theme CSS including variables and any additional styles.
    
    Args:
        theme_config: Theme configuration dictionary from Django settings
        
    Returns:
        Complete CSS string for the theme
    """
    css_parts = []
    
    # Generate CSS variables
    css_parts.append(generate_css_variables(theme_config))
    
    # Future: Add dark mode support
    if theme_config and theme_config.get('dark_mode'):
        css_parts.append(generate_dark_mode_css(theme_config))
    
    return '\n\n'.join(css_parts)


def generate_dark_mode_css(theme_config: Dict[str, Any]) -> str:
    """
    Generate dark mode CSS overrides.
    
    Args:
        theme_config: Theme configuration with dark mode settings
        
    Returns:
        CSS string for dark mode
    """
    # Placeholder for future dark mode implementation
    return """
/* Dark mode support - coming soon */
@media (prefers-color-scheme: dark) {
  :root {
    /* Dark mode color overrides will go here */
  }
}

[data-theme="dark"] {
  /* Manual dark mode toggle support */
}
"""


def generate_inline_theme_style(theme_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a complete <style> tag with theme CSS for inline inclusion.
    
    Args:
        theme_config: Theme configuration dictionary from Django settings
        
    Returns:
        HTML style tag containing theme CSS
    """
    css_content = generate_theme_css(theme_config)
    return f'<style id="spellbook-theme">\n{css_content}\n</style>'


def export_theme_to_json(theme_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Export theme configuration to a JSON-serializable dictionary.
    
    Args:
        theme_config: Theme configuration dictionary
        
    Returns:
        JSON-serializable theme dictionary
    """
    theme = SpellbookTheme(theme_config)
    return theme.to_dict()


def validate_theme_config(theme_config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a theme configuration dictionary.
    
    Args:
        theme_config: Theme configuration to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check structure
    if not isinstance(theme_config, dict):
        errors.append("Theme configuration must be a dictionary")
        return False, errors
    
    # Validate colors if present
    if 'colors' in theme_config:
        if not isinstance(theme_config['colors'], dict):
            errors.append("'colors' must be a dictionary")
        else:
            from .validator import validate_color
            for name, value in theme_config['colors'].items():
                try:
                    validate_color(value)
                except ValueError as e:
                    errors.append(f"Color '{name}': {str(e)}")
    
    # Validate custom colors if present
    if 'custom_colors' in theme_config:
        if not isinstance(theme_config['custom_colors'], dict):
            errors.append("'custom_colors' must be a dictionary")
        else:
            from .validator import validate_color
            for name, value in theme_config['custom_colors'].items():
                try:
                    validate_color(value)
                except ValueError as e:
                    errors.append(f"Custom color '{name}': {str(e)}")
    
    # Validate boolean flags
    if 'generate_variants' in theme_config:
        if not isinstance(theme_config['generate_variants'], bool):
            errors.append("'generate_variants' must be a boolean")
    
    if 'dark_mode' in theme_config:
        if not isinstance(theme_config['dark_mode'], bool):
            errors.append("'dark_mode' must be a boolean")
    
    return len(errors) == 0, errors