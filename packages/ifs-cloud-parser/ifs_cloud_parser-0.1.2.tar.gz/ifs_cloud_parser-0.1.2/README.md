# Tree-sitter PL/SQL IFS

🚀 High-performance parser for IFS Cloud PL/SQL variant

## Status
✅ **100% success rate** on entire IFS Cloud codebase (9,748 files)

## Quick Install

```bash
pip install ifs-cloud-parser
# OR
pip install .
```

## Usage

```python
import ifs_cloud_parser
from tree_sitter import Language, Parser

language = Language(ifs_cloud_parser.language()) 
parser = Parser()
parser.set_language(language)

tree = parser.parse(b"PROCEDURE Test___ IS BEGIN NULL; END;")
print(tree.root_node.sexp())
```

## Requirements
- Python 3.8+
- tree-sitter
- pybind11 (auto-installed)
- C++ compiler

### Windows Requirements
For Windows builds, you need:
- Visual Studio Build Tools 2022 or Visual Studio 2022
- Windows SDK
- Run from "Developer Command Prompt" or "Visual Studio Developer PowerShell"

If build fails on Windows:
```cmd
# Install build tools
pip install --upgrade setuptools wheel pybind11

# Set environment variable
set DISTUTILS_USE_SDK=1

# Build from source
pip install . --verbose
```

## Platform Support
- ✅ Linux (x64, ARM64) - manylinux wheels
- ✅ macOS (Intel, Apple Silicon)  
- ✅ Windows (x64) - requires Visual Studio Build Tools

This parser handles all IFS Cloud PL/SQL variants and custom syntax.
