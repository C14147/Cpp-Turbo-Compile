from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class QMakeAnalyzer(Analyzer):
    """Analyze Qt QMake .pro files and provide targeted suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        pro_files = list(root.rglob('*.pro'))
        suggestions = []

        if not pro_files:
            return {"found": False, "files": [], "suggestions": []}

        for pf in pro_files:
            try:
                text = pf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            # Check for CONFIG entries
            if 'CONFIG +=' not in text and 'CONFIG+=' not in text:
                suggestions.append({
                    'type': 'QMAKE_CONFIG',
                    'file': str(pf),
                    'message': 'QMake .pro file has no CONFIG flags. Consider enabling precompiled headers or optimization flags via CONFIG +='
                })

            # Check for QT modules
            if 'QT +=' in text or 'QT+=' in text:
                suggestions.append({
                    'type': 'QMAKE_QT_MODULES',
                    'file': str(pf),
                    'message': 'Qt modules declared; ensure only needed modules are included to reduce compile and link time.'
                })

        return {"found": True, "files": [str(p) for p in pro_files], "suggestions": suggestions}
