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

# Platform-specific compilation settings
extra_compile_args = []
extra_link_args = []

if sys.platform == 'win32':
    # Windows MSVC settings
    extra_compile_args = [
        '/wd4101',  # unreferenced local variable
        '/wd4189',  # local variable initialized but not referenced
        '/wd4996',  # deprecated function warnings
        '/std:c++14',  # Explicit C++14 standard
        '/DNOMINMAX',  # Prevent min/max macro conflicts
    ]
    extra_link_args = [
        '/MACHINE:X64' if platform.architecture()[0] == '64bit' else '/MACHINE:X86'
    ]
else:
    # Unix-like systems (Linux, macOS)
    extra_compile_args = [
        '-Wno-unused-but-set-variable',
        '-Wno-unused-variable', 
        '-Wno-unused-parameter',
        '-w',  # Suppress warnings
        '-std=c++14',  # Explicit C++14 standard
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

    def build_extension(self, ext):
        # Additional Windows-specific build fixes
        if sys.platform == 'win32':
            # Ensure we're using the correct architecture
            if platform.architecture()[0] == '64bit':
                ext.extra_link_args = ext.extra_link_args or []
                if '/MACHINE:X64' not in ext.extra_link_args:
                    ext.extra_link_args.append('/MACHINE:X64')
            
            # Add Windows-specific library paths if needed
            import distutils.util
            plat_name = distutils.util.get_platform()
            if 'win-amd64' in plat_name or 'win32' in plat_name:
                # Ensure proper linking for Windows
                pass
                
        super().build_extension(ext)

ifs_cloud_parser = Extension(
    'ifs_cloud_parser',
    sources=sources,
    include_dirs=[
        pybind11.get_include(),
        'src',
    ],
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    define_macros=[
        ('PYBIND11_USE_SMART_HOLDER_AS_DEFAULT', '1')  # Better memory management
    ] if sys.platform != 'win32' else []
)

setup(
    ext_modules=[ifs_cloud_parser],
    cmdclass={'build_ext': CustomBuildExt},
)
