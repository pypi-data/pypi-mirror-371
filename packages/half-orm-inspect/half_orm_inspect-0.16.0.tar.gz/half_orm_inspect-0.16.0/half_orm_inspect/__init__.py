"""
half-orm-inspect - Database inspection extension for halfORM

This extension provides comprehensive database inspection and introspection 
capabilities for halfORM, including:

- Database structure inspection
- Relation and schema browsing
- JSON output for programmatic use
- Detailed statistics and metadata

Usage:
    # Through halfORM CLI
    half_orm inspect mydatabase
    half_orm inspect mydatabase public.users
    half_orm inspect mydatabase --schema public --type table
    
    # Standalone (if installed)
    half-orm-inspect mydatabase
"""

import sys
from typing import Optional

# Version management - should match half_orm major.minor
try:
    import half_orm
    _half_orm_version = half_orm.__version__.split('.')
    __version__ = f"{_half_orm_version[0]}.{_half_orm_version[1]}.0"
except ImportError:
    __version__ = "1.0.0"

# Package metadata
__title__ = "half-orm-inspect"
__description__ = "Database inspection extension for halfORM"
__author__ = "halfORM Team"
__author_email__ = "contact@half-orm.org"
__url__ = "https://github.com/half-orm/half-orm-inspect"
__license__ = "MIT"

# Module exports
__all__ = [
    '__version__',
    'check_compatibility',
    'get_extension_info',
]

# Extension metadata for CLI discovery
EXTENSION_INFO = {
    'name': 'inspect',
    'description': 'Database structure inspection and introspection tools',
    'version': __version__,
    'commands': ['inspect'],
    'author': __author__,
    'requires': [f'half_orm>={__version__.rsplit(".", 1)[0]}'],
    'homepage': __url__,
    'license': __license__,
}


def check_compatibility() -> bool:
    """
    Check if this extension is compatible with the installed halfORM version.
    
    Returns:
        bool: True if compatible, False otherwise
    """
    try:
        import half_orm
        
        # Parse versions
        ext_parts = __version__.split('.')
        core_parts = half_orm.__version__.split('.')
        
        if len(ext_parts) < 2 or len(core_parts) < 2:
            return False
        
        # Check major.minor compatibility
        return (ext_parts[0] == core_parts[0] and 
                ext_parts[1] == core_parts[1])
                
    except ImportError:
        return False


def get_extension_info() -> dict:
    """
    Get extension information dictionary.
    
    Returns:
        dict: Extension metadata
    """
    return EXTENSION_INFO.copy()


def _check_runtime_compatibility():
    """
    Check compatibility at import time and warn if incompatible.
    """
    if not check_compatibility():
        try:
            import half_orm
            core_version = half_orm.__version__
            expected_version = f"{__version__.split('.')[0]}.{__version__.split('.')[1]}.x"
            
            print(f"WARNING: half-orm-inspect v{__version__} may not be compatible", 
                  file=sys.stderr)
            print(f"         with half_orm v{core_version}", file=sys.stderr)
            print(f"         Expected half_orm version: {expected_version}", file=sys.stderr)
            print("         Consider upgrading to matching versions", file=sys.stderr)
            
        except ImportError:
            print("WARNING: half_orm not found. This extension requires half_orm.", 
                  file=sys.stderr)


# Optional: Check compatibility at import time
# Uncomment if you want warnings on version mismatches
