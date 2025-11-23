from config.enums import Compiler


COMPILER_CONFIGS = {
    Compiler.GCC: {
        "name": "GCC",
        "pch_ext": ".gch",
        "pch_flags": ["-x", "c++-header"],
        "std_pch_name": "stdafx.h",
        "optimization_flags": ["-O2", "-march=native", "-flto"],
        "debug_flags": ["-g", "-O0"],
        "pgo_flags": ["-fprofile-generate", "-fprofile-use"],
    },
    Compiler.CLANG: {
        "name": "Clang",
        "pch_ext": ".pch",
        "pch_flags": ["-x", "c++-header"],
        "std_pch_name": "stdafx.h",
        "optimization_flags": ["-O2", "-march=native", "-flto=thin"],
        "debug_flags": ["-g", "-O0"],
        "pgo_flags": ["-fprofile-instr-generate", "-fprofile-instr-use"],
    },
    Compiler.MSVC: {
        "name": "MSVC",
        "pch_ext": ".pch",
        "pch_flags": ["/Yc"],
        "std_pch_name": "stdafx.h",
        "optimization_flags": ["/O2", "/GL", "/arch:AVX2"],
        "debug_flags": ["/Zi", "/Od"],
        "pgo_flags": ["/GL", "/LTCG"],
    },
    Compiler.ICC: {
        "name": "Intel C++ Compiler",
        "pch_ext": ".pch",
        "pch_flags": ["-pch-create"],
        "std_pch_name": "stdafx.h",
        "optimization_flags": ["-O2", "-xHost", "-ipo"],
        "debug_flags": ["-g", "-O0"],
        "pgo_flags": ["-prof-gen", "-prof-use"],
    },
}