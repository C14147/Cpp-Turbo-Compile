from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class MSBuildAnalyzer(Analyzer):
    """Analyze MSBuild project files (.vcxproj, .sln) and give suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        proj_files = list(root.rglob('*.vcxproj')) + list(root.rglob('*.sln'))
        suggestions = []

        if not proj_files:
            return {"found": False, "files": [], "suggestions": []}

        for pf in proj_files:
            try:
                text = pf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            if '<ClCompile' in text and 'PrecompiledHeader' not in text:
                suggestions.append({
                    'type': 'MSBUILD_PCH',
                    'file': str(pf),
                    'message': 'Project has C++ compile items but no PrecompiledHeader setting detected. Consider enabling PCH in MSBuild projects.'
                })

        return {"found": True, "files": [str(p) for p in proj_files], "suggestions": suggestions}
