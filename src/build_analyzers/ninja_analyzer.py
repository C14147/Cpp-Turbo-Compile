from pathlib import Path
from typing import Dict, Any

from build_analyzers import Analyzer


class NinjaAnalyzer(Analyzer):
    """Analyze Ninja build files (build.ninja) for common optimizations."""

    def analyze(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path)
        ninja_files = list(root.rglob('build.ninja'))
        suggestions = []

        if not ninja_files:
            return {"found": False, "files": [], "suggestions": []}

        for nf in ninja_files:
            try:
                text = nf.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''

            # Check for pool or jobs
            if 'pool' not in text:
                suggestions.append({
                    'type': 'NINJA_POOL',
                    'file': str(nf),
                    'message': 'No explicit ninja pools found. Consider using pools for expensive steps to limit concurrency.'
                })

        return {"found": True, "files": [str(p) for p in ninja_files], "suggestions": suggestions}
