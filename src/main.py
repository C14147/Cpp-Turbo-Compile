#!/usr/bin/env python3
"""
C++项目编译优化分析器 - 增强优化版
用于分析C++项目结构，检测编译瓶颈并提供优化建议
支持PCH生成、多编译器、多构建系统等高级功能
"""

import os
import argparse
from config import *
from CppProjectAnalyzer import CppProjectAnalyzer


def create_optimization_pipeline(analyzer: CppProjectAnalyzer) -> bool:
    """执行优化流水线"""
    print("🚀 启动优化流水线...")
    
    success = True
    
    # 生成PCH
    if analyzer.optimization_config.generate_pch:
        pch_file = analyzer.generate_pch_header()
        
        # 编译PCH
        if analyzer.optimization_config.compile_pch:
            success &= analyzer.compile_pch()
    
    # 生成构建配置
    configs = analyzer.generate_build_configurations()
    
    # 保存主要构建系统的配置
    main_config = configs.get(analyzer.build_system.value, "")
    if main_config:
        config_file = analyzer.project_path / f"build_optimization_{analyzer.build_system.value}.txt"
        with open(config_file, 'w') as f:
            f.write(main_config)
        print(f"💾 构建配置已保存至: {config_file}")
    
    return success


def main():
    parser = argparse.ArgumentParser(
        description='C++项目分析器 (Cpp-Turbo-Compile) - 提供编译优化建议',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本分析
  python cpp_analyzer.py /path/to/project
  
  # 完整优化流水线
  python cpp_analyzer.py /path/to/project --pch --compile-pch --lto --parallel
  
  # 高级分析配置
  python cpp_analyzer.py /path/to/project --max-includes 30 --max-complexity 60 --parallel-analysis
  
  # 多构建系统支持
  python cpp_analyzer.py /path/to/project --build-system bazel --compiler clang
  
  # 生成JSON报告
  python cpp_analyzer.py /path/to/project --output report.json --format json
        """
    )
    
    # 基本参数
    parser.add_argument('project_path', help='C++项目根目录路径')
    parser.add_argument('-o', '--output', help='输出报告文件路径')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='报告格式')
    
    # 分析配置
    parser.add_argument('--max-includes', type=int, default=20, help='头文件包含数量阈值')
    parser.add_argument('--max-complexity', type=int, default=50, help='文件复杂度阈值') 
    parser.add_argument('--max-header-size', type=int, default=10000, help='头文件大小阈值(字节)')
    parser.add_argument('--pch-max-headers', type=int, default=25, help='PCH中包含的最大头文件数')
    parser.add_argument('--no-template-analysis', action='store_true', help='禁用模板分析')
    parser.add_argument('--no-circular-check', action='store_true', help='禁用循环依赖检查')
    parser.add_argument('--no-unused-check', action='store_true', help='禁用未使用头文件检查')
    parser.add_argument('--no-parallel-analysis', action='store_true', help='禁用并行分析')
    parser.add_argument('--analysis-timeout', type=int, default=30, help='文件分析超时时间(秒)')
    
    # 优化配置
    parser.add_argument('--pch', action='store_true', help='生成预编译头文件')
    parser.add_argument('--compile-pch', action='store_true', help='编译预编译头文件')
    parser.add_argument('--pch-name', default='pch.h', help='预编译头文件名')
    parser.add_argument('--no-lto', action='store_true', help='禁用链接时优化')
    parser.add_argument('--no-ipo', action='store_true', help='禁用过程间优化')
    parser.add_argument('--pgo', action='store_true', help='启用性能导向优化')
    parser.add_argument('--unity-build', action='store_true', help='启用Unity构建')
    parser.add_argument('--no-cache', action='store_true', help='禁用编译缓存')
    parser.add_argument('--no-parallel-build', action='store_true', help='禁用并行构建')
    
    # 系统配置
    parser.add_argument('--compiler', choices=[c.value for c in config.enums.Compiler], default='gcc', 
                       help='指定编译器')
    parser.add_argument('--build-system', choices=[b.value for b in config.enums.BuildSystem], 
                       default='cmake', help='指定构建系统')
    parser.add_argument('--ignore', action='append', dest='ignore_patterns',
                       help='忽略的文件或目录模式 (可多次使用)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"❌ 错误: 路径 '{args.project_path}' 不存在")
        return 1
    
    # 创建配置对象
    analysis_config = AnalysisConfig(
        max_header_includes=args.max_includes,
        max_file_complexity=args.max_complexity,
        max_header_size=args.max_header_size,
        pch_max_headers=args.pch_max_headers,
        enable_template_analysis=not args.no_template_analysis,
        enable_circular_dep_check=not args.no_circular_check,
        enable_unused_header_check=not args.no_unused_check,
        parallel_analysis=not args.no_parallel_analysis,
        analysis_timeout=args.analysis_timeout
    )
    
    optimization_config = OptimizationConfig(
        generate_pch=args.pch,
        compile_pch=args.compile_pch,
        pch_name=args.pch_name,
        enable_lto=not args.no_lto,
        enable_ipo=not args.no_ipo,
        enable_pgo=args.pgo,
        unity_build=args.unity_build,
        cache_compilation=not args.no_cache,
        parallel_build=not args.no_parallel_build
    )
    
    # 创建分析器实例
    analyzer = CppProjectAnalyzer(
        project_path=args.project_path,
        compiler=config.enums.Compiler(args.compiler),
        build_system=config.enums.BuildSystem(args.build_system),
        ignore_patterns=args.ignore_patterns or [],
        analysis_config=analysis_config,
        optimization_config=optimization_config
    )
    
    try:
        # 执行分析
        analyzer.analyze_project()
        
        # 执行优化流水线
        if args.pch or args.compile_pch:
            create_optimization_pipeline(analyzer)
        
        # 生成报告
        analyzer.generate_report(args.output, args.format)
        
        print(f"\n🎉 分析完成！请查看报告获取详细优化建议。")
        
    except KeyboardInterrupt:
        print("\n⚠️  分析被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
