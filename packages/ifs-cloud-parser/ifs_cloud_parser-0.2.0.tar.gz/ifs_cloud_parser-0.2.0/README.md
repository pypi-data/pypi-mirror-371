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

### Basic Usage (tree-sitter 0.25.0)

```python
import ifs_cloud_parser
from tree_sitter import Language, Parser

# Create language and parser
language = Language(ifs_cloud_parser.language())
parser = Parser(language)

# Parse IFS Cloud PL/SQL code
code = b"PROCEDURE Test___ IS BEGIN NULL; END;"
tree = parser.parse(code)

# Explore the syntax tree
print(tree.root_node.sexp())
print(f"Root node type: {tree.root_node.type}")
print(f"Child count: {tree.root_node.child_count}")
```

### Advanced Usage

```python
import ifs_cloud_parser
from tree_sitter import Language, Parser, Node

# Setup parser
language = Language(ifs_cloud_parser.language())
parser = Parser(language)

# Parse complex IFS Cloud code
code = b"""
PROCEDURE Customer_Order_API.Check_Insert___ (
   newrec_ IN OUT NOCOPY customer_order_tab%ROWTYPE,
   indrec_ IN OUT NOCOPY Indicator_Rec,
   attr_   IN OUT VARCHAR2 
) IS
BEGIN
   -- @Override annotation support
   Error_SYS.Check_Not_Null(lu_name_, 'ORDER_NO', newrec_.order_no);
   IF newrec_.state = 'Planned' THEN
      Customer_Order_Line_API.Calculate_Prices___(newrec_.order_no);
   END IF;
END Check_Insert___;
"""

tree = parser.parse(code)

def walk_tree(node: Node, depth=0):
    indent = "  " * depth
    print(f"{indent}{node.type}: {node.text[:50].decode() if node.text else ''}")
    for child in node.children:
        walk_tree(child, depth + 1)

# Print the complete syntax tree
walk_tree(tree.root_node)
```

## Features

- ✅ **Complete IFS Cloud PL/SQL support** - Handles all variants and custom syntax
- 🚀 **High performance** - Built with tree-sitter for speed
- 🔧 **Stable tree-sitter** - Uses tree-sitter 0.25.0 for maximum compatibility
- 📱 **Cross-platform** - Works on Linux, macOS, and Windows
- 🎯 **100% tested** - Validated against entire IFS Cloud codebase

## Requirements
- Python 3.8+
- tree-sitter >= 0.25.0, < 0.26.0 (for maximum compatibility)
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
