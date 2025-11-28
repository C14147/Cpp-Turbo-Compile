from pathlib import Path
from typing import Dict, Any
from build_analyzers import Analyzer


class BazelAnalyzer(Analyzer):
    """Analyze Bazel BUILD files for optimizations and suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        build_files = list(root.rglob('BUILD')) + list(root.rglob('BUILD.bazel'))
        suggestions = []

        if not build_files:
            return {"found": False, "files": [], "suggestions": []}

        for bf in build_files:
            try:
                text = bf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            if 'cc_library' in text and 'pch' not in text:
                suggestions.append({
                    'type': 'BAZEL_PCH',
                    'file': str(bf),
                    'message': 'Bazel BUILD contains cc_library targets. Consider adding settings or macros to enable precompiled headers or thin LTO where appropriate.'
                })

        return {"found": True, "files": [str(p) for p in build_files], "suggestions": suggestions}
