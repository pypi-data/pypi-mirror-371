# Tree-sitter PL/SQL IFS

🚀 High-performance parser for IFS Cloud PL/SQL variant

## Status
✅ **100% success rate** on entire IFS Cloud codebase (9,748 files)

## Quick Install

```bash
pip install tree_sitter_plsql_ifs-*.whl
# OR
pip install .
```

## Usage

```python
import tree_sitter_plsql_ifs
from tree_sitter import Language, Parser

language = Language(tree_sitter_plsql_ifs.language()) 
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

This parser handles all IFS Cloud PL/SQL variants and custom syntax.
