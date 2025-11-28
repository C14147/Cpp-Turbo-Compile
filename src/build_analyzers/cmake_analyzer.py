import os
from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class CMakeAnalyzer(Analyzer):
    """Analyze CMake-specific files (CMakeLists.txt) and provide suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        cmake_files = list(root.rglob('CMakeLists.txt'))
        suggestions = []

        if not cmake_files:
            return {"found": False, "files": [], "suggestions": []}

        for cf in cmake_files:
            try:
                text = cf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            # Check for PCH usage
            if 'target_precompile_headers' not in text and 'precompile' not in text:
                suggestions.append({
                    'type': 'CMAKE_PCH',
                    'file': str(cf),
                    'message': 'CMake project does not appear to use precompiled headers. Consider using target_precompile_headers to reduce compile times.'
                })

            # Check for parallel build hints
            if 'CMAKE_BUILD_PARALLEL_LEVEL' not in text and 'cmake --build' not in text:
                suggestions.append({
                    'type': 'CMAKE_PARALLEL',
                    'file': str(cf),
                    'message': 'No explicit parallel build configuration detected. Consider setting CMAKE_BUILD_PARALLEL_LEVEL or documenting parallel build instructions.'
                })

        return {"found": True, "files": [str(p) for p in cmake_files], "suggestions": suggestions}
