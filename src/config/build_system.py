from config.enums import BuildSystem


BUILD_SYSTEM_CONFIGS = {
    BuildSystem.CMAKE: {
        "name": "CMake",
        "parallel_flag": "--parallel",
        "pch_support": True,
    },
    BuildSystem.QMAKE: {"name": "QMake", "parallel_flag": "-j", "pch_support": True},
    BuildSystem.NINJA: {"name": "Ninja", "parallel_flag": "-j", "pch_support": True},
    BuildSystem.MSBUILD: {
        "name": "MSBuild",
        "parallel_flag": "/m",
        "pch_support": True,
    },
    BuildSystem.MAKE: {"name": "Make", "parallel_flag": "-j", "pch_support": False},
    BuildSystem.BAZEL: {
        "name": "Bazel",
        "parallel_flag": "--jobs",
        "pch_support": False,
    },
    BuildSystem.MESON: {"name": "Meson", "parallel_flag": "-j", "pch_support": True},
}
