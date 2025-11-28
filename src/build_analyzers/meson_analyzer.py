from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class MesonAnalyzer(Analyzer):
    """Analyze meson.build files and provide suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        meson_files = list(root.rglob('meson.build'))
        suggestions = []

        if not meson_files:
            return {"found": False, "files": [], "suggestions": []}

        for mf in meson_files:
            try:
                text = mf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            if "b_lto" not in text and "lto" not in text:
                suggestions.append({
                    'type': 'MESON_LTO',
                    'file': str(mf),
                    'message': 'Meson build files do not enable LTO. Consider adding b_lto=true for release builds to improve performance.'
                })

        return {"found": True, "files": [str(p) for p in meson_files], "suggestions": suggestions}
