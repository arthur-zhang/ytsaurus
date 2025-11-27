# 文档系统

本目录包含 YTsaurus 系统的完整技术文档，支持多语言和多格式输出。

## 目录结构

- **en/** - 英文文档
  - 英文版本的技术文档
  - 包含用户指南、开发文档、API 参考等

- **ru/** - 俄文文档
  - 俄文版本的技术文档
  - 与英文文档内容同步

- **code-examples/** - 代码示例
  - 各种编程语言的使用示例
  - 实际应用场景的代码演示

- **images/** - 文档图片资源
  - 文档中使用的插图、截图
  - 架构图、流程图等视觉资料

- **构建和配置文件**
  - `build-and-serve.sh` - 文档构建和服务启动脚本
  - `presets.yaml` - 文档生成预设配置
  - `redirects.yaml` - 文档重定向映射
  - `ya.make` - 构建系统配置
  - `.yfm` - YFM (Yandex Flavored Markdown) 配置

## 功能特性

### 多语言支持
- 支持英文和俄文文档
- 独立的语言目录结构
- 便于本地化和翻译

### 丰富的文档类型
- 用户指南和教程
- 开发者文档
- API 和 SDK 参考
- 架构设计文档
- 部署和运维指南

### 代码示例库
- 多语言示例 (C++, Python, Java, Go)
- 完整的运行示例
- 最佳实践演示

## 使用方法

### 构建文档
```bash
# 构建所有语言的文档
./build-and-serve.sh --build --lang en,ru

# 构建特定语言
./build-and-serve.sh --build --lang en

# 开发模式 (自动重载)
./build-and-serve.sh --serve --watch
```

### 查看文档
```bash
# 启动本地服务器
./build-and-serve.sh --serve --port 3000

# 访问文档
# English: http://localhost:3000/en/
# Russian: http://localhost:3000/ru/
```

### 添加新内容
1. 在对应语言目录下创建 Markdown 文件
2. 遵循 YFM 格式规范
3. 添加必要的元数据和标签
4. 更新目录索引文件

## 文档架构

### 英文文档 (en/)
- `getting_started/` - 快速入门指南
- `user_guide/` - 用户指南
- `developer/` - 开发者文档
- `api/` - API 参考
- `deployment/` - 部署指南
- `administration/` - 运维管理

### 俄文文档 (ru/)
- `getting_started/` - 快速入门指南
- `user_guide/` - 用户指南
- `developer/` - 开发者文档
- `api/` - API 参考
- `deployment/` - 部署指南
- `administration/` - 运维管理

## 格式规范

### Markdown 扩展
- 使用 YFM (Yandex Flavored Markdown)
- 支持代码块语法高亮
- 自定义扩展语法
- 交叉引用支持

### 文档元数据
```yaml
---
title: 文档标题
description: 文档描述
category: 分类
tags: [标签1, 标签2]
---
```

## 构建系统

### 技术栈
- YFM 文档生成器
- Markdown 源文件
- HTML 静态站点
- 支持主题定制

### 输出格式
- HTML 网站
- PDF 文档
- 单页应用
- 移动端适配

## 依赖项

- Node.js 14+
- YFM CLI 工具
- Python (某些构建脚本)
- Git (版本控制)

## 贡献指南

1. **内容贡献**
   - 遵循现有的文档结构
   - 使用标准的 Markdown 格式
   - 添加必要的示例代码

2. **翻译贡献**
   - 保持与原文档同步
   - 考虑本地化差异
   - 使用一致的技术术语

3. **代码示例**
   - 确保代码可执行
   - 添加必要的注释
   - 包含错误处理