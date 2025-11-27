# Changelog Surgeon

## 项目描述

Changelog Surgeon 是一个专业的 YTsaurus 变更日志（changelog）处理工具。它能够从多个变更日志文件中提取指定序列号范围的记录，并将其合并成一个新的变更日志文件。该工具主要用于分布式系统的数据恢复、日志分析和调试等场景。

## 功能特性

- **多文件合并**：支持同时处理多个变更日志文件
- **精确提取**：基于序列号范围精确提取所需记录
- **数据验证**：确保同一序列号的记录数据一致性
- **高效处理**：支持批量读取和高效内存管理
- **跨平台支持**：支持 Linux 和 macOS 的多个架构

## 文件说明

- `main.cpp` - 主程序源代码，包含了变更日志处理的核心逻辑
- `ya.make` - 构建配置文件，定义了项目依赖关系
- `CMakeLists.*.txt` - CMake 构建配置文件，支持不同平台和架构

## 使用方法

### 编译

```bash
# 使用 ya 工具构建
ya make -t changelog_surgeon

# 或使用 CMake 构建
cmake --build . --target changelog_surgeon
```

### 命令行参数

- `--changelog-list` - 输入的变更日志文件列表，以空格分隔
- `--resulting-changelog-name` - 输出的变更日志文件名
- `--first-sequence-number` - 要提取的起始序列号（可选，自动推断）
- `--last-sequence-number` - 要提取的结束序列号（可选，自动推断）
- `--max-records-per-read` - 每次读取的最大记录数（默认：1,000,000）

### 使用示例

```bash
# 合并多个变更日志文件
./changelog_surgeon \
    --changelog-list "changelog_001.dat changelog_002.dat changelog_003.dat" \
    --resulting-changelog-name merged_changelog.dat

# 提取特定序列号范围的记录
./changelog_surgeon \
    --changelog-list "changelog_001.dat changelog_002.dat" \
    --resulting-changelog-name partial_changelog.dat \
    --first-sequence-number 1000 \
    --last-sequence-number 2000
```

## 实现原理

### 核心算法

1. **序列号范围推断**：自动分析输入文件确定序列号范围
2. **批量读取**：使用 `MaxRecordsPerRead` 参数控制每次读取的记录数
3. **记录去重**：确保同一序列号只保留一条记录
4. **数据验证**：验证重复记录的数据一致性

### 数据结构

- `TSurgeonParams` - 存储命令行参数和配置信息
- `TMutationHeader` - 变更记录头部信息
- `TSharedRef` - 共享数据引用，用于高效内存管理

### 依赖项

- **yt/yt/server/lib/hydra** - 变更日志处理库
- **yt/yt/server/lib/io** - IO 引擎库
- **yt/yt/core** - 核心功能和工具
- **library/cpp/getopt** - 命令行参数解析

## 注意事项

- 输入的变更日志文件必须按顺序排列
- 生成的变更日志最多支持 100,000,000 条记录
- 工具会自动跳过空的变更日志文件
- 确保有足够的磁盘空间存储输出文件

## 错误处理

工具包含完善的错误检查机制：
- 序列号范围验证
- 文件访问权限检查
- 数据完整性验证
- 内存使用限制

## 性能优化

- 使用线程池 IO 引擎提高读取性能
- 支持批量读取减少系统调用
- 智能内存管理避免不必要的拷贝

## 日志输出

工具使用 YTsaurus 日志框架输出详细的执行信息：
- 文件处理进度
- 序列号范围信息
- 错误和警告信息
- 性能统计