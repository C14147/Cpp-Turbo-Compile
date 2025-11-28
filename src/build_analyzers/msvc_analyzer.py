from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class MSVCAnalyzer(Analyzer):
    """Analyze MSVC project files for MSVC-specific optimizations."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        suggestions = []

        for f in root.rglob('*.vcxproj'):
            try:
                text = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue

            if '/GL' not in text and 'LTCG' not in text:
                suggestions.append({
                    'type': 'MSVC_LTO',
                    'file': str(f),
                    'message': 'MSVC whole program optimization (/GL) or LTCG not detected. Consider enabling these for release builds.'
                })

        return {"found": True, "files": [], "suggestions": suggestions}
