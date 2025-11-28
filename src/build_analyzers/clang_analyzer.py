from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class ClangAnalyzer(Analyzer):
    """Analyze project files for Clang specific flags and suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        suggestions = []

        for f in root.rglob('*'):
            if f.suffix in {'.cmake', '.mk', '.make', '.pro', '.txt'}:
                try:
                    text = f.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                if '-flto' not in text and '-flto=thin' not in text:
                    suggestions.append({
                        'type': 'CLANG_LTO',
                        'file': str(f),
                        'message': 'Clang LTO flags not detected. Consider enabling -flto or -flto=thin for link-time optimizations.'
                    })

        return {"found": True, "files": [], "suggestions": suggestions}
