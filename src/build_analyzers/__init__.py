"""Build and compiler analyzer package

Contains analyzers for various build systems and compilers. Each analyzer
exposes an `analyze(project_path: str) -> dict` method that returns a dict
with keys: `found` (bool), `files` (list), `suggestions` (list).

This module provides:
- `Analyzer`: an abstract base class describing the analyzer API
- `get_build_analyzer(project_path: Optional[str], build_system: Optional[config.enums.BuildSystem])`
  which returns an Analyzer subclass (or None) based on a user-provided
  `build_system` or by detecting project files under `project_path`.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Optional, Type

from config import enums


class Analyzer:
    """Minimal Analyzer interface.

    Concrete analyzers should subclass this and implement `analyze()`.
    The `analyze()` method returns a dict with at least a `suggestions` key
    containing a list of suggestion dicts.
    """

    def analyze(self, project_path: str) -> dict:
        """Analyze the project at `project_path` and return results.

        Override in subclasses.
        """
        raise NotImplementedError()


# Import concrete analyzers after defining Analyzer to avoid circular imports
from .cmake_analyzer import CMakeAnalyzer
from .qmake_analyzer import QMakeAnalyzer
from .ninja_analyzer import NinjaAnalyzer
from .msbuild_analyzer import MSBuildAnalyzer
from .make_analyzer import MakeAnalyzer
from .bazel_analyzer import BazelAnalyzer
from .meson_analyzer import MesonAnalyzer

# Compiler analyzers (exported for completeness)
from .gcc_analyzer import GCCAnalyzer
from .clang_analyzer import ClangAnalyzer
from .msvc_analyzer import MSVCAnalyzer
from .icc_analyzer import ICCAnalyzer


__all__ = [
    "CMakeAnalyzer",
    "QMakeAnalyzer",
    "NinjaAnalyzer",
    "MSBuildAnalyzer",
    "MakeAnalyzer",
    "BazelAnalyzer",
    "MesonAnalyzer",
    "GCCAnalyzer",
    "ClangAnalyzer",
    "MSVCAnalyzer",
    "ICCAnalyzer",
    "Analyzer",
    "get_build_analyzer",
]


# Mapping from BuildSystem enum to analyzer class
_BUILD_ANALYZER_MAP = {
    enums.BuildSystem.CMAKE: CMakeAnalyzer,
    enums.BuildSystem.QMAKE: QMakeAnalyzer,
    enums.BuildSystem.NINJA: NinjaAnalyzer,
    enums.BuildSystem.MSBUILD: MSBuildAnalyzer,
    enums.BuildSystem.MAKE: MakeAnalyzer,
    enums.BuildSystem.BAZEL: BazelAnalyzer,
    enums.BuildSystem.MESON: MesonAnalyzer,
}


def _detect_build_system_from_files(project_path: Optional[str]) -> Optional[enums.BuildSystem]:
    """Try to detect the build system by presence of typical files.

    Returns a `config.enums.BuildSystem` or None if unknown.
    """
    if not project_path:
        return None
    p = Path(project_path)
    if not p.exists():
        return None

    # Common detection heuristics
    # Check top-level and recursive files
    if (p / "CMakeLists.txt").exists() or any(p.glob("**/CMakeLists.txt")):
        return enums.BuildSystem.CMAKE
    if any(p.glob("**/*.pro")):
        return enums.BuildSystem.QMAKE
    if (p / "BUILD").exists() or (p / "WORKSPACE").exists() or any(p.glob("**/BUILD")):
        return enums.BuildSystem.BAZEL
    if (p / "meson.build").exists() or any(p.glob("**/meson.build")):
        return enums.BuildSystem.MESON
    if (p / "Makefile").exists() or any(p.glob("**/Makefile")):
        return enums.BuildSystem.MAKE
    if (p / "build.ninja").exists() or any(p.glob("**/build.ninja")):
        return enums.BuildSystem.NINJA
    if any(p.glob("**/*.sln")) or any(p.glob("**/*.vcxproj")):
        return enums.BuildSystem.MSBUILD

    # Additional heuristics: autoconf, scons
    if (p / "configure.ac").exists() or any(p.glob("**/configure.ac")) or (p / "configure").exists():
        return enums.BuildSystem.MAKE
    if (p / "SConstruct").exists() or any(p.glob("**/SConstruct")):
        return enums.BuildSystem.MAKE

    # Check .gitmodules and examine submodule paths if present
    gitmodules = p / ".gitmodules"
    if gitmodules.exists():
        try:
            content = gitmodules.read_text(encoding="utf-8", errors="ignore")
            # simple parse for path = entries
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("path ="):
                    subpath = line.split("=", 1)[1].strip()
                    candidate = p / subpath
                    if candidate.exists():
                        detected = _detect_build_system_from_files(str(candidate))
                        if detected:
                            return detected
        except Exception:
            pass

    return None


def get_build_analyzer(project_path: Optional[str] = None, build_system: Optional[enums.BuildSystem] = None) -> Optional[Type[Analyzer]]:
    """Return an Analyzer class for the given build_system or by detecting it.

    Priority: if `build_system` is provided, return the mapped analyzer. If
    not, detect by inspecting `project_path` files. Returns None when no
    suitable analyzer is found.
    """
    # If user provided explicit build system, prefer it
    if build_system is not None:
        analyzer = _BUILD_ANALYZER_MAP.get(build_system)
        if analyzer:
            return analyzer

    # Fallback to automatic detection
    detected = _detect_build_system_from_files(project_path)
    if detected is not None:
        return _BUILD_ANALYZER_MAP.get(detected)

    # Nothing detected
    return None

