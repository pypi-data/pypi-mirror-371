"""
Tests for smooth_import package
"""

import pytest
from smooth_import import PackageImporter, resolve_import


class TestPackageImporter:
    """Test cases for PackageImporter class"""
    
    def test_importer_initialization(self):
        """Test that PackageImporter can be initialized"""
        importer = PackageImporter(verbose=False)
        assert importer is not None
        assert hasattr(importer, 'resolve_import')
    
    def test_importer_with_verbose(self):
        """Test that PackageImporter works with verbose mode"""
        importer = PackageImporter(verbose=True)
        assert importer.verbose is True


class TestResolveImport:
    """Test cases for resolve_import function"""
    
    def test_resolve_import_function_exists(self):
        """Test that resolve_import function is available"""
        assert callable(resolve_import)
    
    def test_resolve_import_signature(self):
        """Test that resolve_import has the expected signature"""
        import inspect
        sig = inspect.signature(resolve_import)
        params = list(sig.parameters.keys())
        assert 'entrypoint_filepath' in params
        assert 'object_name' in params
        assert 'verbose' in params


class TestPackageVersion:
    """Test cases for package version and metadata"""
    
    def test_version_attribute(self):
        """Test that __version__ is properly set"""
        from smooth_import import __version__
        assert __version__ == "1.0.0"
    
    def test_author_attributes(self):
        """Test that author information is properly set"""
        from smooth_import import __author__, __email__
        assert __author__ == "Sawradip Saha"
        assert __email__ == "sawradip0@gmail.com"
    
    def test_all_export(self):
        """Test that __all__ exports the expected items"""
        from smooth_import import __all__
        expected_exports = ['PackageImporter', 'resolve_import']
        assert all(item in __all__ for item in expected_exports)


if __name__ == "__main__":
    pytest.main([__file__]) 