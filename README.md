# C++ Turbo Compile - C++项目编译优化分析器

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue" alt="Python版本">
  <img src="https://img.shields.io/badge/license-Apache-green" alt="许可证">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="平台支持">
</p>

## 🚀 项目简介

C++ Turbo Compile 是一个强大的C++项目编译优化分析工具，专门用于分析C++项目结构、检测编译瓶颈并提供针对性的优化建议。它能够帮助开发者显著提升大型C++项目的编译速度，优化构建流程。

### 核心功能

- 🔍 **全面项目分析** - 深度扫描C++项目，分析头文件依赖关系、循环依赖、未使用头文件等
- ⚡ **编译时间估算** - 基于文件大小和复杂度准确估算每个源文件的编译时间
- 📊 **性能瓶颈检测** - 识别影响编译速度的关键因素和潜在问题
- 🎯 **智能优化建议** - 提供具体可行的优化方案，包括预编译头文件(PCH)、并行构建等
- 🛠️ **多编译器支持** - 完全支持GCC、Clang、MSVC、Intel C++等多种主流编译器
- 🏗️ **多构建系统支持** - 兼容CMake、Make、Ninja、QMake、MSBuild、Bazel、Meson等构建系统

## 🌟 主要特性

### 多编码支持
支持包括UTF-8、GBK、GB2312、Big5、Shift-JIS等多种编码格式的源文件，确保在不同环境下都能正确分析项目。

### 预编译头文件(PCH)生成
智能分析项目中最常用的头文件，自动生成优化的预编译头文件，显著减少编译时间。

### 并行分析与构建
充分利用多核CPU性能，支持并行分析和构建，进一步提升处理速度。

### 模板使用分析
深度分析项目中模板的使用情况，帮助识别可能导致编译时间增加的复杂模板代码。

### 循环依赖检测
自动检测并报告项目中的循环依赖问题，帮助改善代码结构。

## 📦 支持的编译器和构建系统

### 编译器支持
- **GCC** - GNU编译器集合
- **Clang** - LLVM编译器前端
- **MSVC** - Microsoft Visual C++编译器
- **ICC** - Intel C++编译器

### 构建系统支持
- **CMake** - 跨平台构建系统
- **Make** - 经典Unix构建工具
- **Ninja** - 小型构建系统，专注于速度
- **QMake** - Qt项目构建工具
- **MSBuild** - Microsoft构建引擎
- **Bazel** - Google开源构建工具
- **Meson** - 高性能构建系统

## 🚀 快速开始

### 环境要求
- Python 3.7 或更高版本
- 支持的C++编译器（GCC/Clang/MSVC/ICC等）

### 安装方法
```bash
# 克隆项目
git clone <repository-url>
cd cpp-turbo-compile

# 直接运行（无需额外安装）
```

### 基本使用

```bash
# 基本分析
python main.py /path/to/your/cpp/project

# 生成预编译头文件
python main.py /path/to/your/cpp/project --pch

# 完整优化流水线
python main.py /path/to/your/cpp/project --pch --compile-pch --lto --parallel

# 指定编译器和构建系统
python main.py /path/to/your/cpp/project --compiler clang --build-system cmake

# 输出报告到文件
python main.py /path/to/your/cpp/project -o analysis_report.txt
```

### 高级配置

```bash
# 调整分析参数
python main.py /path/to/your/cpp/project \
  --max-includes 30 \
  --max-complexity 60 \
  --max-header-size 15000 \
  --parallel-analysis

# 启用特定优化
python main.py /path/to/your/cpp/project \
  --unity-build \
  --pgo \
  --lto

# 忽略特定目录或文件
python main.py /path/to/your/cpp/project \
  --ignore build \
  --ignore third_party \
  --ignore "*.test.*"
```

## 📈 分析报告示例

工具会生成详细的分析报告，包括：

- 📊 项目整体统计信息
- ⚠️ 检测到的问题列表（按严重程度分类）
- 💡 优化建议（按优先级排序）
- ⏱️ 各文件编译时间估算
- 📁 头文件依赖关系图
- 📏 代码复杂度分析

## 🛠️ 技术架构

```
cpp-turbo-compile/
├── main.py                 # 程序入口和命令行接口
├── CppProjectAnalyzer.py   # 核心分析引擎
├── config/                 # 配置文件目录
│   ├── __init__.py         # 配置模块初始化
│   ├── enums.py            # 枚举类型定义
│   ├── compiler.py         # 编译器配置
│   ├── build_system.py     # 构建系统配置
│   ├── pch.py              # 预编译头文件优化
│   └── lib_buildtime_patterns.py  # 库编译时间模式
└── README.md               # 项目说明文档
```

## 🎯 优化建议类型

1. **预编译头文件建议** - 推荐应该包含在PCH中的常用头文件
2. **未使用头文件清理** - 检测并建议删除未使用的头文件
3. **循环依赖消除** - 提供解决循环依赖的具体方案
4. **PIMPL模式应用** - 建议对大型头文件使用PIMPL模式
5. **统一头文件管理** - 优化头文件组织结构
6. **构建系统优化** - 并行编译、缓存编译等建议

## 📄 许可证

本项目采用Apache 2.0许可证，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📧 联系方式

如有问题或建议，请创建Issue或通过邮箱联系项目维护者。