# Error Skeleton (错误骨架)

错误骨架是 YTsaurus 中用于错误分析和聚类的重要工具，通过提取错误的核心特征来生成标准化、可比较的错误表示。

## 概述

错误骨架系统的主要功能：
- 递归聚合错误树中的错误码和消息
- 标准化可变信息（如GUID、路径、时间戳等）
- 生成适合错误聚类的骨架字符串
- 去重和排序内部错误
- 支持嵌套错误结构

## 核心功能

### 1. 错误指纹生成
通过正则表达式替换，将错误消息中的可变信息标准化为通用占位符：

#### 替换规则
- **GUID**: 匹配格式为 `xxxx-xxxx-xxxx-xxxx` 的字符串 → `<guid>`
- **路径**: 匹配 `//` 开头的路径 → `<path>`
- **地址**: 匹配 YP-C 地址格式 → `<address>`
- **键值**: `Key "xxx"` → `Key <key>`
- **时间戳**: `Timestamp xxx` → `Timestamp <timestamp>`
- **账户**: `Account "xxx"` → `Account <account>`
- **属性**: `Attribute "xxx"` → `Attribute <attribute>`
- **引用**: `Reference "xxx"` → `Reference <reference>`
- **分号**: 移除所有分号

### 2. 骨架构建算法
1. **提取错误指纹**: 将错误消息标准化
2. **递归处理内部错误**: 对每个内部错误生成骨架
3. **去重**: 移除重复的内部错误骨架
4. **排序**: 对内部错误骨架进行排序
5. **组合**: 组合主错误和内部错误形成最终骨架

## 主要接口

```cpp
// 生成错误骨架
std::string GetErrorSkeleton(const TError& error);
```

## 使用示例

### 基本使用
```cpp
TError error(1001, "Failed to read chunk #123-456-789-abc from //tmp/data");
// 原始错误信息包含具体的chunk ID和路径

auto skeleton = GetErrorSkeleton(error);
// 结果: "#1001: Failed to read chunk <guid> from <path>"
```

### 嵌套错误
```cpp
TError outerError(2001, "Transaction failed");
outerError.InnerErrors().push_back(TError(1001, "Chunk not found: #123-456-789-abc"));
outerError.InnerErrors().push_back(TError(1002, "Permission denied for user: john_doe"));

auto skeleton = GetErrorSkeleton(outerError);
// 结果: "#2001: Transaction failed @ [#1001: Chunk not found: <guid>; #1002: Permission denied for user: <key>]"
```

## 应用场景

### 1. 错误监控和告警
- 将相似的错误分组
- 减少告警风暴
- 识别高频错误模式

### 2. 问题诊断
- 快速识别错误类型
- 追踪错误传播路径
- 分析错误关联关系

### 3. 自动化处理
- 基于错误骨架的自动恢复
- 错误分类和路由
- 智能重试策略

### 4. 数据分析
- 错误趋势分析
- 系统健康度评估
- 性能瓶颈识别

## 性能考虑

### 计算复杂度
- 时间复杂度: O(n log n)，其中n是错误树中的节点数
- 空间复杂度: O(n)，用于存储中间结果

### 优化建议
1. **缓存机制**: 对相同错误缓存骨架
2. **异步处理**: 在后台线程生成骨架
3. **批量处理**: 批量处理多个错误
4. **惰性计算**: 按需生成骨架

## 最佳实践

### 1. 错误设计
- 使用有意义的错误码
- 提供清晰但标准化的错误消息
- 合理组织错误层次结构

### 2. 监控集成
```cpp
// 在错误处理中使用骨架
catch (const TError& error) {
    auto skeleton = GetErrorSkeleton(error);

    // 记录到监控系统
    MonitoringSystem->RecordError(skeleton);

    // 基于骨架的告警
    if (IsCriticalError(skeleton)) {
        AlertManager->TriggerAlert(error);
    }
}
```

### 3. 聚类策略
- 基于骨架的前缀匹配
- 时间窗口内的错误计数
- 结合服务拓扑的上下文信息

## 扩展性

### 添加新的替换规则
```cpp
// 在 Replacements 中添加新的模式
{&NewPattern(), "<replacement>"}
```

### 自定义骨架生成
- 继承 `GetErrorSkeleton` 函数
- 添加业务特定的标准化规则
- 实现自定义聚类算法

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- RE2 正则表达式库 (`contrib/libs/re2/`)
- 字符串工具库 (`library/cpp/yt/misc/`)

## 注意事项

1. **性能影响**: 避免在热路径频繁调用
2. **消息格式**: 确保错误消息格式一致
3. **正则表达式**: 注意正则表达式的性能
4. **内存使用**: 大量错误处理时注意内存管理
5. **线程安全**: 函数是线程安全的，可在多线程环境使用

## 示例输出

```
原始错误:
  #501: Transaction lock wait timeout for transaction #123-456-789-abc at //home/user/table

错误骨架:
  #501: Transaction lock wait timeout for transaction <guid> at <path>

带嵌套错误:
  #600: Operation failed @ [#100: Chunk not found: <guid>; #200: Permission denied: <account>; #300: Timeout: <timestamp>]
```