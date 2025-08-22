"""
smooth_import - Enhanced package importer for Python projects

A robust package importer that handles complex import patterns including:
- Relative imports without __init__.py
- Mixed package and standalone structures  
- Dynamic import resolution
- Automatic import rewriting
"""

from .importer import PackageImporter

__version__ = "1.0.0"
__author__ = "Sawradip Saha"
__email__ = "sawradip0@gmail.com"

# Convenience function for quick usage
def resolve_import(entrypoint_filepath: str, object_name: str, verbose: bool = True):
    """
    Convenience function to quickly resolve an import.
    
    Args:
        entrypoint_filepath (str): Path to the Python file containing the target object
        object_name (str): Name of the object to import
        verbose (bool): Whether to print verbose logging
    
    Returns:
        Any: The resolved object
    """
    importer = PackageImporter(verbose=verbose)
    return importer.resolve_import(entrypoint_filepath, object_name)

# Export main classes and functions
__all__ = ['PackageImporter', 'resolve_import']