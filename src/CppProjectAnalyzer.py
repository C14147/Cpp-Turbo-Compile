import re
import json
import time
import subprocess
import fnmatch
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
import multiprocessing
import concurrent.futures
from config import *


class CppProjectAnalyzer:
    def __init__(self, 
                 project_path: str,
                 compiler: config.enums.Compiler = config.enums.Compiler.GCC,
                 build_system: config.enums.BuildSystem = config.enums.BuildSystem.CMAKE,
                 ignore_patterns: Optional[List[str]] = None,
                 analysis_config: Optional[AnalysisConfig] = None,
                 optimization_config: Optional[OptimizationConfig] = None):
        
        self.project_path = Path(project_path).resolve()
        self.compiler = compiler
        self.build_system = build_system
        self.ignore_patterns = ignore_patterns or []
        
        self.analysis_config = analysis_config or AnalysisConfig()
        self.optimization_config = optimization_config or OptimizationConfig()
        
        # 分析数据
        self.files = []
        self.include_graph = defaultdict(set)
        self.dependency_count = defaultdict(int)
        self.file_sizes = {}
        self.header_frequency = Counter()
        self.template_usage = Counter()
        self.circular_deps = []
        self.unused_headers = set()
        self.issues = []
        self.suggestions = []
        self.build_times_estimate = {}
        
        # 编译器特定配置
        self.compiler_config = config.compiler.COMPILER_CONFIGS
        
        # 构建系统配置
        self.build_system_config = config.build_system.BUILD_SYSTEM_CONFIGS

    def discover_files(self) -> List[Path]:
        """发现项目中的所有C++文件"""
        print("🔍 扫描C++项目文件...")
        
        cpp_extensions = {'.cpp', '.cc', '.cxx', '.c++', '.C'}
        header_extensions = {'.h', '.hpp', '.hh', '.hxx', '.h++', '.inl'}
        
        all_files = []
        for ext in cpp_extensions | header_extensions:
            pattern = f'**/*{ext}'
            for file_path in self.project_path.glob(pattern):
                if not self._should_ignore_file(file_path):
                    all_files.append(file_path)
                
        self.files = sorted(all_files)
        print(f"📁 找到 {len(self.files)} 个C++文件")
        return self.files
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """检查是否应该忽略该文件"""
        default_ignore_patterns = {
            'build/', 'cmake-build-', '.git/', 'third_party/', 
            'external/', 'test/', 'tests/', 'benchmark/', 'vendor/',
            'node_modules/', '__pycache__/', '.vscode/', '.vs/',
            'Debug/', 'Release/', 'x64/', 'x86/'
        }
        
        # 合并默认忽略模式和用户指定的模式
        all_ignore_patterns = default_ignore_patterns | set(self.ignore_patterns)
        file_str = str(file_path.relative_to(self.project_path))
        
        return any(fnmatch.fnmatch(file_str, pattern) for pattern in all_ignore_patterns)

    def analyze_project(self) -> Dict[str, Any]:
        """执行完整项目分析"""
        start_time = time.time()
        
        print("🚀 开始分析C++项目...")
        
        # 文件发现
        self.discover_files()
        
        # 并行分析
        if self.analysis_config.parallel_analysis:
            self._parallel_analyze_files()
        else:
            self._sequential_analyze_files()
        
        # 高级分析
        if self.analysis_config.enable_circular_dep_check:
            self._detect_circular_dependencies()
            
        if self.analysis_config.enable_unused_header_check:
            self._detect_unused_headers()
            
        if self.analysis_config.enable_template_analysis:
            self._analyze_template_usage()
        
        # 生成建议
        self.generate_suggestions()
        
        # 估算编译时间
        self._estimate_build_times()
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  分析完成，耗时: {elapsed_time:.2f} 秒")
        
        return self._get_analysis_summary()

    def _parallel_analyze_files(self):
        """并行分析文件"""
        print("📊 并行分析文件...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            # 分析头文件包含关系
            future_to_file = {
                executor.submit(self._analyze_file_includes, file_path): file_path 
                for file_path in self.files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    future.result(timeout=self.analysis_config.analysis_timeout)
                except concurrent.futures.TimeoutError:
                    print(f"⏰ 分析超时: {file_path}")
                except Exception as e:
                    print(f"⚠️  分析失败 {file_path}: {e}")

    def _sequential_analyze_files(self):
        """顺序分析文件"""
        print("📊 顺序分析文件...")
        
        for file_path in self.files:
            try:
                self._analyze_file_includes(file_path)
            except Exception as e:
                print(f"⚠️  分析失败 {file_path}: {e}")

    def _analyze_file_includes(self, file_path: Path):
        """分析单个文件的包含关系"""
        include_pattern = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[">]')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 分析文件大小
            self.file_sizes[file_path] = len(content)
            
            # 查找包含的头文件
            includes = include_pattern.findall(content)
            for included in includes:
                # 记录头文件使用频率
                self.header_frequency[included] += 1
                
                # 尝试解析实际文件路径
                resolved_path = self._resolve_include_path(file_path, included)
                if resolved_path:
                    self.include_graph[file_path].add(resolved_path)
                    self.dependency_count[resolved_path] += 1
                    
            # 检测问题
            self._detect_file_issues(file_path, content)
                    
        except Exception as e:
            print(f"⚠️  无法分析文件 {file_path}: {e}")

    def _resolve_include_path(self, source_file: Path, include_name: str) -> Optional[Path]:
        """解析包含路径到实际文件"""
        # 系统头文件
        if include_name.startswith('<') and '>' in include_name:
            return None
            
        # 相对路径包含
        if include_name.startswith('"'):
            include_name = include_name.strip('"')
            candidate = source_file.parent / include_name
            if candidate.exists():
                return candidate
                
        # 在项目目录中搜索
        for ext in ['', '.h', '.hpp', '.hh', '.hxx']:
            candidate_path = include_name + ext if ext else include_name
            candidate = self.project_path / candidate_path
            if candidate.exists():
                return candidate
                
            # 在子目录中搜索
            for header_file in self.project_path.rglob(candidate_path):
                if header_file.is_file():
                    return header_file
                    
        return None

    def _detect_file_issues(self, file_path: Path, content: str):
        """检测文件级别的编译问题"""
        include_count = len(re.findall(r'^\s*#\s*include', content, re.MULTILINE))
        complexity_score = self._calculate_complexity(content)
        file_size = len(content)
        
        # 过多的头文件包含
        if include_count > self.analysis_config.max_header_includes:
            self.issues.append({
                'type': 'EXCESSIVE_INCLUDES',
                'file': str(file_path),
                'severity': config.enums.Severity.MEDIUM,
                'message': f'文件包含 {include_count} 个头文件（超过阈值 {self.analysis_config.max_header_includes}）',
                'suggestion': '使用前置声明替代不必要的头文件包含，考虑使用PIMPL模式'
            })
        
        # 高复杂性文件
        if complexity_score > self.analysis_config.max_file_complexity:
            self.issues.append({
                'type': 'HIGH_COMPLEXITY',
                'file': str(file_path),
                'severity': config.enums.Severity.HIGH,
                'message': f'文件复杂性较高 (分数: {complexity_score})，可能显著增加编译时间',
                'suggestion': '考虑拆分文件或减少模板使用'
            })
        
        # 大型头文件
        if file_path.suffix in {'.h', '.hpp', '.hh'} and file_size > self.analysis_config.max_header_size:
            self.issues.append({
                'type': 'LARGE_HEADER',
                'file': str(file_path),
                'severity': config.enums.Severity.MEDIUM,
                'message': f'头文件较大 ({file_size} 字节)，影响包含它的所有编译单元',
                'suggestion': '拆分头文件或使用前置声明，考虑使用PIMPL模式'
            })

    def _calculate_complexity(self, content: str) -> int:
        """计算文件的复杂性分数"""
        complexity = 0
        
        # 模板使用
        if self.analysis_config.enable_template_analysis:
            template_pattern = re.compile(r'template\s*<[^>]*>')
            complexity += len(template_pattern.findall(content)) * 3
            
            # 模板特化/偏特化
            template_specialization = re.compile(r'template\s*<>\s*[^;{]+')
            complexity += len(template_specialization.findall(content)) * 2
        
        # 头文件包含数量
        include_pattern = re.compile(r'^\s*#\s*include', re.MULTILINE)
        complexity += len(include_pattern.findall(content))
        
        # 类定义
        class_pattern = re.compile(r'(class|struct)\s+\w+')
        complexity += len(class_pattern.findall(content)) * 2
        
        # 函数定义
        function_pattern = re.compile(r'(\w+)\s+\w+\s*\([^)]*\)\s*(\{|\[\[[^\]]*\]\])')
        complexity += len(function_pattern.findall(content))
        
        # 宏定义
        macro_pattern = re.compile(r'^\s*#\s*define\s+\w+', re.MULTILINE)
        complexity += len(macro_pattern.findall(content)) * 0.5
        
        return int(complexity)

    def _detect_circular_dependencies(self):
        """检测循环依赖"""
        print("🔄 检测循环依赖...")
        
        visited = set()
        recursion_stack = set()
        
        def dfs(file_path):
            if file_path in recursion_stack:
                # 找到循环依赖
                cycle_start = list(recursion_stack).index(file_path)
                cycle = list(recursion_stack)[cycle_start:]
                self.circular_deps.append(cycle)
                return
            
            if file_path in visited:
                return
            
            visited.add(file_path)
            recursion_stack.add(file_path)
            
            for dependency in self.include_graph.get(file_path, set()):
                dfs(dependency)
            
            recursion_stack.remove(file_path)
        
        for file_path in self.files:
            if file_path not in visited:
                dfs(file_path)
        
        if self.circular_deps:
            for i, cycle in enumerate(self.circular_deps):
                self.issues.append({
                    'type': 'CIRCULAR_DEPENDENCY',
                    'file': f"Cycle {i+1}",
                    'severity': config.enums.Severity.HIGH,
                    'message': f'检测到循环依赖: {" -> ".join(str(f) for f in cycle)}',
                    'suggestion': '打破循环依赖，使用前置声明或重构代码结构'
                })

    def _detect_unused_headers(self):
        """检测未使用的头文件"""
        print("🔍 检测未使用的头文件...")
        
        # 所有被包含的头文件
        included_headers = set()
        for dependencies in self.include_graph.values():
            included_headers.update(dependencies)
        
        # 项目中的所有头文件
        all_headers = {f for f in self.files if f.suffix in {'.h', '.hpp', '.hh'}}
        
        # 找到未被包含的头文件
        self.unused_headers = all_headers - included_headers
        
        for header in self.unused_headers:
            self.issues.append({
                'type': 'UNUSED_HEADER',
                'file': str(header),
                'severity': config.enums.Severity.LOW,
                'message': '头文件未被任何源文件包含',
                'suggestion': '考虑删除或检查是否需要此头文件'
            })

    def _analyze_template_usage(self):
        """分析模板使用情况"""
        print("📐 分析模板使用...")
        
        template_patterns = [
            (r'template\s*<[^>]*>', "模板声明"),
            (r'std::\w+\s*<[^>]*>', "STL模板"),
            (r'boost::\w+\s*<[^>]*>', "Boost模板"),
        ]
        
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, description in template_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        self.template_usage[description] += len(matches)
            except Exception:
                continue

    def _estimate_build_times(self):
        """估算构建时间"""
        print("⏱️  估算构建时间...")
        
        base_compile_time_per_line = 0.001  # 秒/行（经验值）
        
        for file_path in self.files:
            if file_path.suffix in {'.cpp', '.cc', '.cxx'}:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    
                    complexity = self._calculate_complexity(open(file_path).read())
                    dependency_penalty = len(self.include_graph.get(file_path, set())) * 0.1
                    
                    # 估算编译时间
                    estimated_time = (lines * base_compile_time_per_line * 
                                    (1 + complexity * 0.01) * (1 + dependency_penalty))
                    
                    self.build_times_estimate[file_path] = estimated_time
                    
                except Exception:
                    self.build_times_estimate[file_path] = 0

    def generate_pch_header(self, pch_name: str = None) -> Path:
        """生成预编译头文件"""
        pch_name = pch_name or self.optimization_config.pch_name
        print(f"🎯 生成预编译头文件: {pch_name}")
        
        # 获取最常用的头文件
        max_headers = self.analysis_config.pch_max_headers
        common_headers = self.header_frequency.most_common(max_headers)
        
        pch_content = f"""// pch.h - Generated Precompiled Header
// Generated by C++ Project Analyzer (Cpp-Turbo-Compile)
// Generate Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
// config.enums.Compiler: {self.compiler.value}
// Build System: {self.build_system.value}
// Project: {self.project_path.name}

#pragma once

// The most useful system headers
"""
        
        # 分离系统头文件和项目头文件
        system_headers = []
        project_headers = []
        
        for header, count in common_headers:
            if header.startswith('<') or '/' in header or any(header.endswith(ext) for ext in ['.h', '.hpp']):
                if any(pattern in header for pattern in ['<', '>', '.h']):
                    system_headers.append((header, count))
            else:
                project_headers.append((header, count))
        
        # 添加系统头文件
        for header, count in system_headers:
            if header.startswith('<'):
                pch_content += f"#include {header}  // times: {count}\n"
            else:
                pch_content += f'#include "{header}"  // times: {count}\n'
        
        # 添加项目头文件
        if project_headers:
            pch_content += "\n// Project headers\n"
            for header, count in project_headers:
                pch_content += f'#include "{header}"  // time: {count}\n'
        
        compiler_config = self.compiler_config.get(self.compiler, self.compiler_config[config.enums.Compiler.GCC])
        
        pch_content += config.pch.PCH_SPECIAL_OPT
        
        pch_file = self.project_path / pch_name
        with open(pch_file, 'w', encoding='utf-8') as f:
            f.write(pch_content)
        
        print(f"✅ 预编译头文件已生成: {pch_file}")
        return pch_file

    def compile_pch(self, pch_name: str = None) -> bool:
        """编译预编译头文件"""
        pch_name = pch_name or self.optimization_config.pch_name
        print(f"🔨 编译预编译头文件: {pch_name}")
        
        pch_file = self.project_path / pch_name
        if not pch_file.exists():
            print(f"❌ 预编译头文件不存在: {pch_file}")
            return False
        
        compiler_config = self.compiler_config.get(self.compiler, self.compiler_config[config.enums.Compiler.GCC])
        
        try:
            if self.compiler in [config.enums.Compiler.GCC, config.enums.Compiler.CLANG, config.enums.Compiler.ICC]:
                # GCC/Clang/ICC PCH编译
                pch_output = pch_file.with_suffix(compiler_config["pch_ext"])
                cmd = [
                    self.compiler.value, 
                    *compiler_config["pch_flags"],
                    "-std=c++17",
                    "-O2",
                    "-I.", f"-I{self.project_path}",
                    "-o", str(pch_output),
                    str(pch_file)
                ]
                
                # 添加特定编译器优化
                if self.optimization_config.enable_lto:
                    cmd.append("-flto")
                
                result = subprocess.run(cmd, cwd=self.project_path, 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 预编译头文件编译成功: {pch_output}")
                    return True
                else:
                    print(f"❌ 预编译头文件编译失败: {result.stderr}")
                    return False
                    
            elif self.compiler == config.enums.Compiler.MSVC:
                # MSVC PCH编译 (简化版本)
                print("ℹ️  MSVC PCH编译需要Visual Studio环境")
                print("   请手动在Visual Studio中配置预编译头文件")
                return False
                
        except Exception as e:
            print(f"❌ 编译预编译头文件时出错: {e}")
            return False

    def generate_build_configurations(self) -> Dict[str, str]:
        """生成构建系统配置"""
        print(f"⚙️  生成 {self.build_system.value} 配置")
        
        config_generators = {
            config.enums.BuildSystem.CMAKE: self._generate_cmake_config,
            config.enums.BuildSystem.QMAKE: self._generate_qmake_config,
            config.enums.BuildSystem.NINJA: self._generate_ninja_config,
            config.enums.BuildSystem.MSBUILD: self._generate_msbuild_config,
            config.enums.BuildSystem.MAKE: self._generate_make_config,
            config.enums.BuildSystem.BAZEL: self._generate_bazel_config,
            config.enums.BuildSystem.MESON: self._generate_meson_config
        }
        
        configs = {}
        for build_sys, generator in config_generators.items():
            configs[build_sys.value] = generator()
        
        return configs

    def _generate_cmake_config(self) -> str:
        """生成CMake配置"""
        pch_config = ""
        if self.optimization_config.generate_pch:
            pch_config = f"""
# 预编译头文件配置
target_precompile_headers(${{PROJECT_NAME}} PRIVATE {self.optimization_config.pch_name})
"""
        
        lto_config = ""
        if self.optimization_config.enable_lto:
            lto_config = """
# 链接时优化
include(CheckIPOSupported)
check_ipo_supported(RESULT IPO_SUPPORTED OUTPUT IPO_ERROR)
if(IPO_SUPPORTED)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
"""
        
        parallel_config = ""
        if self.optimization_config.parallel_build:
            parallel_config = """
# 并行编译
if(NOT MSVC)
    find_program(CCACHE_PROGRAM ccache)
    if(CCACHE_PROGRAM)
        set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ${CCACHE_PROGRAM})
        set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ${CCACHE_PROGRAM})
    endif()
endif()
"""
        
        config = f"""
# CMake配置 - 由C++项目分析器自动生成
# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

# 编译器优化
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(${{PROJECT_NAME}} PRIVATE
        -O3
        -DNDEBUG
        -march=native
    )
else()
    target_compile_options(${{PROJECT_NAME}} PRIVATE
        -O0
        -g3
        -Wall
        -Wextra
    )
endif()

{pch_config}
{lto_config}
{parallel_config}

# 并行构建
set(CMAKE_BUILD_PARALLEL_LEVEL ${{CMAKE_SYSTEM_PROCESSOR_COUNT}})
"""
        return config

    def _generate_qmake_config(self) -> str:
        """生成QMake配置"""
        return f"""
# QMake配置 - 自动生成
CONFIG += c++17 precompile_header
PRECOMPILED_HEADER = {self.optimization_config.pch_name}

# 编译器优化
QMAKE_CXXFLAGS_RELEASE += -O3 -march=native
QMAKE_CXXFLAGS_DEBUG += -O0 -g

# 并行编译
unix {{
    QMAKE_CXXFLAGS += -j$$system(nproc)
}}

# MSVC特定设置
win32:msvc {{
    PRECOMPILED_HEADER = {self.optimization_config.pch_name}
}}
"""

    def _generate_ninja_config(self) -> str:
        """生成Ninja配置"""
        return f"""
# Ninja构建配置 - 需要配合CMake使用
# 在CMake中启用预编译头文件，Ninja会自动处理并行编译

# 手动编译PCH的命令:
# {self.compiler.value} -x c++-header {self.optimization_config.pch_name} -o {self.optimization_config.pch_name}{self.compiler_config.get(self.compiler, {}).get('pch_ext', '.gch')}

# 优化构建
pool = console
builddir = build

# 并行构建
ninja_required_version = 1.7
"""

    def _generate_msbuild_config(self) -> str:
        """生成MSBuild配置"""
        return f"""
<!-- MSBuild配置 - 自动生成 -->
<PropertyGroup>
  <PrecompiledHeader>Create</PrecompiledHeader>
  <PrecompiledHeaderFile>{self.optimization_config.pch_name}</PrecompiledHeaderFile>
  <MultiProcessorCompilation>true</MultiProcessorCompilation>
  <Optimization>MaxSpeed</Optimization>
  <IntrinsicFunctions>true</IntrinsicFunctions>
  <FunctionLevelLinking>true</FunctionLevelLinking>
</PropertyGroup>

<ItemDefinitionGroup>
  <ClCompile>
    <PrecompiledHeader>Use</PrecompiledHeader>
    <WarningLevel>Level4</WarningLevel>
    <Optimization>MaxSpeed</Optimization>
  </ClCompile>
</ItemDefinitionGroup>
"""

    def _generate_make_config(self) -> str:
        """生成Makefile配置"""
        return f"""
# Makefile配置 - 自动生成
CXX = {self.compiler.value}
CXXFLAGS = -std=c++17 -I. -Wall -Wextra
PCH_HEADER = {self.optimization_config.pch_name}
PCH_FILE = $(PCH_HEADER){self.compiler_config.get(self.compiler, {}).get('pch_ext', '.gch')}

# 预编译头文件规则
$(PCH_FILE): $(PCH_HEADER)
\t$(CXX) -x c++-header $(CXXFLAGS) $(PCH_HEADER) -o $(PCH_FILE)

# 包含PCH的编译规则
%.o: %.cpp $(PCH_FILE)
\t$(CXX) $(CXXFLAGS) -include $(PCH_HEADER) -c $< -o $@

# 并行编译
JOBS := $(shell nproc 2>/dev/null || echo 4)

build: $(PCH_FILE)
\t$(MAKE) -j$(JOBS) all

# 清理
clean:
\trm -f $(PCH_FILE) *.o
"""

    def _generate_bazel_config(self) -> str:
        """生成Bazel配置"""
        return """
# Bazel配置 - 自动生成
# 在BUILD文件中添加以下配置:

# cc_library(
#     name = "pch",
#     hdrs = ["pch.h"],
#     copts = ["-include", "pch.h"],
# )

# 并行构建
build --jobs=$(nproc 2>/dev/null || echo 4)
build --compilation_mode=opt
build --copt=-O3
"""

    def _generate_meson_config(self) -> str:
        """生成Meson配置"""
        return f"""
# Meson配置 - 自动生成
project('{self.project_path.name}', 'cpp',
  version : '1.0',
  default_options : [
    'warning_level=3',
    'cpp_std=c++17',
    'buildtype=release',
    'optimization=3',
    'b_lto=true',
    'b_pch=true'
  ]
)

# 预编译头文件
pch = declare_dependency(
  compile_args: ['-include', '{self.optimization_config.pch_name}']
)

# 并行构建
meson.add_install_script('post_install.py')
"""

    def generate_suggestions(self):
        """生成优化建议"""
        print("💡 生成优化建议...")
        
        # 基于分析结果生成建议
        self._suggest_forward_declarations()
        self._suggest_pimpl_pattern()
        self._suggest_unified_headers()
        self._suggest_build_optimizations()
        self._suggest_compiler_specific_optimizations()
        self._suggest_code_restructuring()
        self._suggest_caching_strategies()

    def _suggest_forward_declarations(self):
        """建议使用前置声明"""
        highly_included_headers = [
            header for header, count in self.dependency_count.items() 
            if count > 5 and header.suffix in {'.h', '.hpp', '.hh'}
        ]
        
        for header in highly_included_headers:
            self.suggestions.append({
                'type': 'FORWARD_DECLARATION',
                'target': str(header),
                'priority': config.enums.Severity.HIGH,
                'description': f'该头文件被 {self.dependency_count[header]} 个文件包含，考虑使用前置声明',
                'action': f'在依赖此头文件的源文件中使用 class {header.stem}; 替代包含'
            })

    def _suggest_pimpl_pattern(self):
        """建议使用PIMPL模式"""
        large_headers = [
            file for file, size in self.file_sizes.items()
            if size > 15000 and file.suffix in {'.h', '.hpp', '.hh'}
        ]
        
        for header in large_headers:
            self.suggestions.append({
                'type': 'PIMPL_PATTERN',
                'target': str(header),
                'priority': config.enums.Severity.MEDIUM,
                'description': f'大型头文件 {header.stem} 适合使用PIMPL模式',
                'action': '实现Pointer to Implementation模式隐藏实现细节'
            })

    def _suggest_unified_headers(self):
        """建议统一头文件"""
        header_files = [f for f in self.files if f.suffix in {'.h', '.hpp', '.hh'}]
        
        for header in header_files:
            content = ""
            try:
                with open(header, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
                
            # 检查是否主要是前置声明
            forward_decls = len(re.findall(r'^\s*(class|struct)\s+\w+;', content, re.MULTILINE))
            includes = len(re.findall(r'^\s*#\s*include', content, re.MULTILINE))
            
            if forward_decls > 5 and includes < 3:
                self.suggestions.append({
                    'type': 'UNIFIED_HEADER',
                    'target': str(header),
                    'priority': config.enums.Severity.LOW,
                    'description': f'检测到前置声明头文件，可统一管理类型声明',
                    'action': '考虑将此文件作为项目的前向声明统一入口'
                })

    def _suggest_build_optimizations(self):
        """建议构建优化"""
        cpu_count = multiprocessing.cpu_count()
        
        build_suggestions = [
            {
                'type': 'BUILD_OPTIMIZATION',
                'target': 'PROJECT',
                'priority': config.enums.Severity.HIGH,
                'description': f'使用{self.build_system.value}并行编译',
                'action': f'使用 {self._get_parallel_build_command()} 进行并行编译'
            }
        ]
        
        if self.optimization_config.cache_compilation:
            build_suggestions.append({
                'type': 'BUILD_OPTIMIZATION', 
                'target': 'PROJECT',
                'priority': config.enums.Severity.MEDIUM,
                'description': '使用ccache/sccache加速编译',
                'action': '安装并配置ccache: sudo apt install ccache && export CC="ccache gcc"'
            })
            
        if self.optimization_config.unity_build:
            build_suggestions.append({
                'type': 'BUILD_OPTIMIZATION',
                'target': 'PROJECT',
                'priority': config.enums.Severity.MEDIUM,
                'description': '使用Unity Build减少编译单元',
                'action': '合并多个源文件到一个编译单元以减少重复包含'
            })
        
        self.suggestions.extend(build_suggestions)

    def _suggest_compiler_specific_optimizations(self):
        """建议编译器特定优化"""
        compiler_suggestions = {
            config.enums.Compiler.GCC: [
                {
                    'type': 'COMPILER_OPTIMIZATION',
                    'target': 'GCC',
                    'priority': config.enums.Severity.MEDIUM,
                    'description': '使用链接时优化(LTO)',
                    'action': '添加编译选项: -flto -O2'
                },
                {
                    'type': 'COMPILER_OPTIMIZATION',
                    'target': 'GCC', 
                    'priority': config.enums.Severity.LOW,
                    'description': '使用PGO优化',
                    'action': '分阶段编译: 1) -fprofile-generate 2) 运行程序 3) -fprofile-use'
                }
            ],
            config.enums.Compiler.CLANG: [
                {
                    'type': 'COMPILER_OPTIMIZATION', 
                    'target': 'Clang',
                    'priority': config.enums.Severity.MEDIUM,
                    'description': '使用ThinLTO优化',
                    'action': '添加编译选项: -flto=thin -O2'
                }
            ],
            config.enums.Compiler.MSVC: [
                {
                    'type': 'COMPILER_OPTIMIZATION',
                    'target': 'MSVC',
                    'priority': config.enums.Severity.MEDIUM, 
                    'description': '启用全程序优化',
                    'action': '添加编译选项: /GL /O2'
                }
            ],
            config.enums.Compiler.ICC: [
                {
                    'type': 'COMPILER_OPTIMIZATION',
                    'target': 'ICC',
                    'priority': config.enums.Severity.MEDIUM,
                    'description': '使用Interprocedural Optimization',
                    'action': '添加编译选项: -ipo -O3'
                }
            ]
        }
        
        self.suggestions.extend(compiler_suggestions.get(self.compiler, []))

    def _suggest_code_restructuring(self):
        """建议代码重构"""
        # 基于编译时间估算的重构建议
        slow_files = sorted(
            [(f, t) for f, t in self.build_times_estimate.items() if t > 1.0],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for file_path, est_time in slow_files:
            self.suggestions.append({
                'type': 'CODE_RESTRUCTURING',
                'target': str(file_path),
                'priority': config.enums.Severity.MEDIUM,
                'description': f'文件编译时间预估较长 ({est_time:.2f}s)',
                'action': '考虑拆分文件或优化包含关系'
            })

    def _suggest_caching_strategies(self):
        """建议缓存策略"""
        if self.optimization_config.cache_compilation:
            self.suggestions.append({
                'type': 'CACHING_STRATEGY',
                'target': 'PROJECT',
                'priority': config.enums.Severity.MEDIUM,
                'description': '配置分布式编译缓存',
                'action': '考虑使用distcc或icecc进行分布式编译'
            })

    def _get_parallel_build_command(self) -> str:
        """获取并行构建命令"""
        commands = {
            config.enums.BuildSystem.CMAKE: "cmake --build . --parallel",
            config.enums.BuildSystem.MAKE: "make -j$(nproc)",
            config.enums.BuildSystem.NINJA: "ninja -j$(nproc)", 
            config.enums.BuildSystem.QMAKE: "make -j$(nproc)",
            config.enums.BuildSystem.MSBUILD: "msbuild /m",
            config.enums.BuildSystem.BAZEL: "bazel build --jobs=$(nproc)",
            config.enums.BuildSystem.MESON: "ninja -j$(nproc)"  # Meson通常使用Ninja作为后端
        }
        return commands.get(self.build_system, "make -j$(nproc)")

    def _get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        header_files = [f for f in self.files if f.suffix in {'.h', '.hpp', '.hh'}]
        source_files = [f for f in self.files if f.suffix in {'.cpp', '.cc', '.cxx'}]
        
        total_estimated_build_time = sum(self.build_times_estimate.values())
        
        return {
            'project_info': {
                'path': str(self.project_path),
                'compiler': self.compiler.value,
                'build_system': self.build_system.value,
                'total_files': len(self.files),
                'header_files': len(header_files),
                'source_files': len(source_files),
                'estimated_build_time': total_estimated_build_time
            },
            'analysis_results': {
                'issues_found': len(self.issues),
                'suggestions': len(self.suggestions),
                'circular_deps': len(self.circular_deps),
                'unused_headers': len(self.unused_headers),
                'most_used_headers': dict(self.header_frequency.most_common(10)),
                'template_usage': dict(self.template_usage)
            }
        }

    def generate_report(self, output_file: Optional[str] = None, format: str = "text") -> Dict[str, Any]:
        """生成分析报告"""
        summary = self._get_analysis_summary()
        
        if format == "json":
            report = {
                'summary': summary,
                'issues': self.issues,
                'suggestions': self.suggestions,
                'detailed_analysis': {
                    'file_complexity': {
                        str(f): self._calculate_complexity(open(f).read()) 
                        for f in self.files if f.exists()
                    },
                    'build_time_estimates': {
                        str(f): t for f, t in self.build_times_estimate.items()
                    }
                }
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"💾 JSON报告已保存至: {output_file}")
            
            return report
        
        else:  # text format
            print("\n" + "="*70)
            print("📊 C++项目编译优化分析报告")
            print("="*70)
            
            proj_info = summary['project_info']
            analysis_results = summary['analysis_results']
            
            print(f"\n📈 项目统计:")
            print(f"   项目路径: {proj_info['path']}")
            print(f"   编译器: {proj_info['compiler']}")
            print(f"   构建系统: {proj_info['build_system']}")
            print(f"   总文件数: {proj_info['total_files']}")
            print(f"   头文件: {proj_info['header_files']}")
            print(f"   源文件: {proj_info['source_files']}")
            print(f"   预估编译时间: {proj_info['estimated_build_time']:.2f}s")
            
            # 显示最常用的头文件
            if analysis_results['most_used_headers']:
                print(f"\n📋 最常用的头文件:")
                for header, count in analysis_results['most_used_headers'].items():
                    print(f"   {header}: {count} 次")
            
            # 问题报告
            if self.issues:
                print(f"\n❌ 检测到 {len(self.issues)} 个问题:")
                for issue in self.issues:
                    severity_icon = {
                        config.enums.Severity.LOW: "🔵",
                        config.enums.Severity.MEDIUM: "🟡", 
                        config.enums.Severity.HIGH: "🔴"
                    }.get(issue['severity'], "⚪")
                    
                    print(f"   {severity_icon} [{issue['severity'].name}] {issue['file']}")
                    print(f"       {issue['message']}")
                    print(f"       💡 建议: {issue['suggestion']}")
            else:
                print(f"\n✅ 未发现严重编译问题")
            
            # 优化建议
            if self.suggestions:
                print(f"\n💡 优化建议 ({len(self.suggestions)} 个):")
                
                # 按优先级分组
                high_priority = [s for s in self.suggestions if s['priority'] == config.enums.Severity.HIGH]
                medium_priority = [s for s in self.suggestions if s['priority'] == config.enums.Severity.MEDIUM]
                low_priority = [s for s in self.suggestions if s['priority'] == config.enums.Severity.LOW]
                
                if high_priority:
                    print("\n   🔴 高优先级:")
                    for suggestion in high_priority:
                        print(f"      {suggestion['description']}")
                        print(f"      → {suggestion['action']}")
                
                if medium_priority:
                    print("\n   🟡 中优先级:")  
                    for suggestion in medium_priority:
                        print(f"      {suggestion['description']}")
                        print(f"      → {suggestion['action']}")
                
                if low_priority:
                    print("\n   🔵 低优先级:")
                    for suggestion in low_priority:
                        print(f"      {suggestion['description']}")
                        print(f"      → {suggestion['action']}")
            
            # 保存报告
            if output_file and format == "text":
                self._save_text_report(output_file, summary)
            
            return summary

    def _save_text_report(self, output_file: str, summary: Dict[str, Any]):
        """保存文本报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("C++项目编译优化分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 写入摘要
            proj_info = summary['project_info']
            f.write("项目摘要:\n")
            f.write(f"  项目路径: {proj_info['path']}\n")
            f.write(f"  编译器: {proj_info['compiler']}\n")
            f.write(f"  构建系统: {proj_info['build_system']}\n")
            f.write(f"  总文件数: {proj_info['total_files']}\n")
            f.write(f"  预估编译时间: {proj_info['estimated_build_time']:.2f}s\n\n")
            
            # 写入问题
            if self.issues:
                f.write(f"检测到的问题 ({len(self.issues)} 个):\n")
                for issue in self.issues:
                    f.write(f"  [{issue['severity'].name}] {issue['file']}\n")
                    f.write(f"     问题: {issue['message']}\n")
                    f.write(f"     建议: {issue['suggestion']}\n\n")
            
            # 写入建议
            if self.suggestions:
                f.write(f"优化建议 ({len(self.suggestions)} 个):\n")
                for suggestion in self.suggestions:
                    f.write(f"  [{suggestion['priority'].name}] {suggestion['description']}\n")
                    f.write(f"     操作: {suggestion['action']}\n\n")
        
        print(f"💾 文本报告已保存至: {output_file}")
