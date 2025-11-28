from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class MakeAnalyzer(Analyzer):
    """Analyze Makefiles for parallel build and PCH hints."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        makefiles = list(root.rglob('Makefile')) + list(root.rglob('makefile'))
        suggestions = []

        if not makefiles:
            return {"found": False, "files": [], "suggestions": []}

        for mf in makefiles:
            try:
                text = mf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            if 'PCH_HEADER' not in text and 'precompiled' not in text.lower():
                suggestions.append({
                    'type': 'MAKE_PCH',
                    'file': str(mf),
                    'message': 'Makefile does not show precompiled header rules. Consider adding a rule to generate and use PCH to speed up builds.'
                })

            if '$(MAKE) -j' not in text and 'nproc' not in text:
                suggestions.append({
                    'type': 'MAKE_PARALLEL',
                    'file': str(mf),
                    'message': 'Makefile lacks explicit parallel invocation guidance. Consider documenting make -j$(nproc) or adding a JOBS variable.'
                })

        return {"found": True, "files": [str(p) for p in makefiles], "suggestions": suggestions}
