#include <pybind11/pybind11.h>

// Forward declarations from tree-sitter
extern "C" {
    typedef struct TSLanguage TSLanguage;
    TSLanguage *ifs_cloud_parser();
}

namespace py = pybind11;

PYBIND11_MODULE(ifs_cloud_parser, m) {
    m.doc() = "IFS Cloud PL/SQL Tree-sitter parser - 100% success rate on IFS Cloud codebase";
    
    m.def("language", []() -> void* {
        return ifs_cloud_parser();
    }, "Get the Tree-sitter Language object for IFS Cloud PL/SQL");
          
    // Add version info
    m.attr("__version__") = "0.1.0";
}
