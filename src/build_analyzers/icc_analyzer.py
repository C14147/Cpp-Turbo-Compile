from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class ICCAnalyzer(Analyzer):
    """Analyze for Intel ICC compiler specific suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        suggestions = []

        for f in root.rglob('*'):
            if f.suffix in {'.cmake', '.mk', '.make', '.pro', '.txt'}:
                try:
                    text = f.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                if '-ipo' not in text and '-xHost' not in text:
                    suggestions.append({
                        'type': 'ICC_OPTS',
                        'file': str(f),
                        'message': 'Intel ICC optimization flags like -ipo or -xHost not detected. Consider enabling compiler-specific flags for performance.'
                    })

        return {"found": True, "files": [], "suggestions": suggestions}
