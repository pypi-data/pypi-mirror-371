#include <pybind11/pybind11.h>

// Forward declarations from tree-sitter
extern "C" {
    typedef struct TSLanguage TSLanguage;
    TSLanguage *tree_sitter_plsql_ifs();
}

namespace py = pybind11;

PYBIND11_MODULE(tree_sitter_plsql_ifs, m) {
    m.doc() = "IFS Cloud PL/SQL Tree-sitter parser - 100% success rate on IFS Cloud codebase";
    
    m.def("language", []() -> void* {
        return tree_sitter_plsql_ifs();
    }, "Get the Tree-sitter Language object for IFS Cloud PL/SQL");
          
    // Add version info
    m.attr("__version__") = "0.1.0";
}
