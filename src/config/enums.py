from enum import Enum


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class BuildSystem(Enum):
    CMAKE = "cmake"
    QMAKE = "qmake"
    NINJA = "ninja"
    MSBUILD = "msbuild"
    MAKE = "make"
    BAZEL = "bazel"
    MESON = "meson"


class Compiler(Enum):
    GCC = "gcc"
    CLANG = "clang"
    MSVC = "msvc"
    ICC = "icc"  # Intel C++ Compiler
    