from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11
import os
import sys
import platform

# Check for scanner.c
sources = ['binding.cc', 'src/parser.c']
if os.path.exists('src/scanner.c'):
    sources.append('src/scanner.c')

# Suppress common tree-sitter warnings and the C++14 flag warning
extra_compile_args = []
if sys.platform != 'win32':
    extra_compile_args = [
        '-Wno-unused-but-set-variable',  # Suppresses: variable 'eof' set but not used
        '-Wno-unused-variable',
        '-Wno-unused-parameter',
        '-w',  # Suppress the '-std=c++14' is valid for C++/ObjC++ but not for C warning
    ]
else:
    # Windows MSVC
    extra_compile_args = [
        '/wd4101',  # unreferenced local variable
        '/wd4189',  # local variable initialized but not referenced  
    ]

class CustomBuildExt(build_ext):
    def finalize_options(self):
        super().finalize_options()
        # Fix platform tag for PyPI compatibility
        if hasattr(self, 'plat_name'):
            # Convert linux_x86_64 to manylinux1_x86_64 for PyPI
            if self.plat_name == 'linux_x86_64':
                self.plat_name = 'manylinux1_x86_64'
            elif self.plat_name == 'linux_aarch64':
                self.plat_name = 'manylinux1_aarch64'

tree_sitter_plsql_ifs = Extension(
    'tree_sitter_plsql_ifs',
    sources=sources,
    include_dirs=[
        pybind11.get_include(),
        'src',
    ],
    language='c++',
    extra_compile_args=extra_compile_args,
)

setup(
    ext_modules=[tree_sitter_plsql_ifs],
    cmdclass={'build_ext': CustomBuildExt},
)
