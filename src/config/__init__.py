from dataclasses import dataclass
import config.enums
import config.pch
import config.compiler
import config.build_system


@dataclass
class AnalysisConfig:
    """分析配置"""

    max_header_includes: int = 20
    max_file_complexity: int = 50
    max_header_size: int = 10000  # bytes
    pch_max_headers: int = 25
    enable_template_analysis: bool = True
    enable_circular_dep_check: bool = True
    enable_unused_header_check: bool = True
    parallel_analysis: bool = True
    analysis_timeout: int = 30  # seconds per file


@dataclass
class OptimizationConfig:
    """优化配置"""

    generate_pch: bool = False
    compile_pch: bool = False
    pch_name: str = "pch.h"
    enable_lto: bool = True
    enable_ipo: bool = True  # Interprocedural Optimization
    enable_pgo: bool = False  # Profile Guided Optimization
    unity_build: bool = False
    cache_compilation: bool = True
    parallel_build: bool = True
    