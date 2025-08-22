# smooth_import

[![PyPI version](https://badge.fury.io/py/smooth_import.svg)](https://badge.fury.io/py/smooth_import)
[![Python versions](https://img.shields.io/pypi/pyversions/smooth_import.svg)](https://pypi.org/project/smooth_import/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enhanced package importer for Python that handles complex import patterns including:

- ✅ Relative imports without `__init__.py`
- ✅ Mixed package and standalone structures
- ✅ Dynamic import resolution
- ✅ Automatic import rewriting
- ✅ Circular dependency handling

## Installation

```bash
pip install smooth_import
```

## Quick Start

```python
from smooth_import import resolve_import

# Resolve an import from a specific file
my_function = resolve_import("path/to/my_module.py", "my_function")
```

## Features

- **Smart Import Resolution**: Automatically handles complex import patterns
- **No __init__.py Required**: Works with modern Python projects that don't use `__init__.py` files
- **Mixed Package Support**: Handles both package and standalone module structures
- **Dynamic Import Rewriting**: Automatically rewrites imports to work correctly
- **Circular Dependency Handling**: Safely handles circular import scenarios

## Usage Examples

### Basic Usage

```python
from smooth_import import resolve_import, PackageImporter

# Using the convenience function
my_function = resolve_import("path/to/my_module.py", "my_function")

# Using the PackageImporter class directly
importer = PackageImporter(verbose=True)
result = importer.resolve_import("path/to/my_module.py", "my_function")
```

### Advanced Usage

```python
from smooth_import import PackageImporter

# Create an importer with custom settings
importer = PackageImporter(verbose=False)

# Resolve imports from complex project structures
try:
    my_class = importer.resolve_import("src/myproject/modules/utils.py", "MyClass")
    print(f"Successfully imported: {my_class}")
except ImportError as e:
    print(f"Import failed: {e}")
```

## Development

This project uses modern Python packaging with `pyproject.toml`. The redundant `setup.py` has been removed for cleaner project structure.

### Building and Publishing

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

3. **Test the build locally**:
   ```bash
   pip install dist/smooth_import-1.0.0.tar.gz
   ```

4. **Upload to PyPI** (replace with your PyPI credentials):
   ```bash
   twine upload dist/*
   ```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sawradip/smooth_import.git
cd smooth_import

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/sawradip/smooth_import)
2. Open an [issue](https://github.com/sawradip/smooth_import/issues)
3. Review the [examples](examples/) directory

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history. 