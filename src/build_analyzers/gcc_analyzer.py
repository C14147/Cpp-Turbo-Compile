from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class GCCAnalyzer(Analyzer):
    """Analyze project files for GCC specific flags and suggestions."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        files = list(root.rglob('*'))
        suggestions = []

        # Look for common GCC flags in CMake, Makefile, etc.
        for f in files:
            if f.suffix in {'.txt', '.cmake', '.mk', '.make', '.pro', '.txt', '.cfg'}:
                try:
                    text = f.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                if '-march=native' not in text:
                    suggestions.append({
                        'type': 'GCC_OPT',
                        'file': str(f),
                        'message': 'GCC optimization flags like -march=native are not present. Consider adding appropriate optimization flags for release builds.'
                    })

        return {"found": True, "files": [], "suggestions": suggestions}
