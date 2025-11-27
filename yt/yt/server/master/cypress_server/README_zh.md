# Cypress Server 组件

## 概述

Cypress Server 是 YTsaurus 系统中实现分层命名空间和元数据管理的核心组件。它提供了一个类似 Unix 文件系统的树形结构，用于组织和管理系统中的所有对象（表、文件、账户、用户等）。Cypress 支持事务性操作、版本控制、访问控制、节点链接等高级特性，是 YTsaurus 元数据管理的基石。

## 核心功能

### 1. 分层命名空间
- **树形结构**: 提供层次化的命名空间组织
- **节点类型**: 支持多种节点类型（Map、List、Document、Link 等）
- **路径解析**: 支持 YPath 路径语言进行复杂查询
- **动态创建**: 运行时动态创建和删除节点

### 2. 事务支持
- **ACID 事务**: 完全支持 ACID 特性的事务
- **快照隔离**: 提供快照隔离级别
- **嵌套事务**: 支持嵌套事务结构
- **两阶段提交**: 分布式事务的两阶段提交

### 3. 版本控制
- **多版本**: 节点的多版本存储
- **历史查询**: 查询节点的历史版本
- **版本比较**: 比较不同版本的差异
- **回滚操作**: 支持版本回滚

### 4. 访问控制
- **ACL**: 基于访问控制列表的权限管理
- **继承**: 权限的继承机制
- **细粒度控制**: 支持操作级别的权限控制
- **审计**: 完整的访问审计日志

## 关键组件

### Cypress Manager (cypress_manager.h/cpp)
- Cypress Server 的核心管理器（195KB）
- 管理所有 Cypress 节点的生命周期
- 处理节点的创建、删除、修改操作
- 维护节点的版本和事务信息
- 提供 YPath 服务接口

### Node (node.h/cpp)
- 节点的基础类定义
- 实现节点的通用属性和行为
- 支持节点的序列化和反序列化
- 管理节点的父子关系

### Node Proxy (node_proxy.h/cpp)
- 节点的代理实现，提供 RPC 接口（131KB）
- 实现节点的远程访问接口
- 处理节点的操作请求
- 提供节点的查询和修改功能

### Composite Node (composite_node.h/cpp)
- 复合节点实现（Map、List 等）
- 支持子节点的管理
- 实现节点的层次结构
- 提供批量操作支持

### Lock (lock.h/cpp)
- 节点锁的实现
- 支持多种锁类型（共享、独占、意向锁）
- 实现死锁检测和预防
- 管理锁的升级和降级

## 文件说明

### 核心管理文件
- `cypress_manager.cpp/h`: Cypress 管理器主实现
- `node.cpp/h`: 节点基类定义
- `node_detail.cpp/h`: 节点详细信息实现
- `node-inl.h`: 节点内联函数

### 节点类型实现文件
- `composite_node.cpp/h`: 复合节点（Map/List）
- `document_node.cpp/h`: 文档节点
- `link_node.cpp/h`: 链接节点
- `portal_entrance_node.cpp/h`: Portal 入口节点

### 代理实现文件
- `node_proxy.cpp/h`: 节点代理基类
- `node_proxy_detail.cpp/h`: 代理详细实现（131KB）
- `composite_node_proxy.cpp`: 复合节点代理
- `document_node_proxy.cpp`: 文档节点代理

### 类型处理文件
- `type_handler.h/cpp`: 类型处理器基类
- `node_type_handler_base.cpp/h`: 节点类型处理器基类
- `map_node_type_handler.cpp/h`: Map 节点类型处理器
- `list_node_type_handler.cpp/h`: List 节点类型处理器

### 访问控制文件
- `access_control_object.cpp/h`: 访问控制对象
- `access_control_object_namespace.cpp/h`: AC 对象命名空间
- `access_control_object_proxy.cpp/h`: AC 对象代理（27KB）
- `access_tracker.cpp/h`: 访问跟踪器

### 特殊功能文件
- `expiration_tracker.cpp/h`: 过期跟踪器（33KB）
- `grafting_manager.cpp/h`: 嫁接管理器（24KB）
- `cypress_traverser.cpp/h`: Cypress 遍历器
- `lock.cpp/h`: 锁管理实现

### Portal 相关文件
- `portal_manager.cpp/h`: Portal 管理器
- `portal_exit_node.cpp/h`: Portal 出口节点
- `portal_entrance_proxy.cpp/h`: Portal 入口代理

### 其他文件
- `helpers.cpp/h`: 辅助函数（21KB）
- `config.cpp/h`: 配置管理
- `private.h`: 私有定义
- `public.h`: 公共接口定义

## 使用方法

### 创建节点
```cpp
// 创建 Map 节点
auto mapNode = cypressManager->CreateNode(
    EObjectType::MapNode,
    transaction
);

// 设置节点属性
mapNode->SetParent(parentNode);
mapNode->SetPath("/path/to/node");
mapNode->SetAccount(account);

// 提交事务
transactionManager->CommitTransaction(transaction);
```

### 修改节点
```cpp
// 开始事务
auto transaction = transactionManager->StartTransaction();

// 锁定节点
auto lock = cypressManager->LockNode(
    node,
    ELockMode::Exclusive,
    transaction
);

// 修改属性
node->SetAttribute("key", value);

// 提交修改
transactionManager->CommitTransaction(transaction);
```

### 查询节点
```cpp
// 解析路径
auto path = TYPath("/path/to/node");
auto resolvedNode = cypressManager->ResolvePath(
    path,
    transaction
);

// 获取属性
auto value = resolvedNode->GetAttribute("key");

// 遍历子节点
for (const auto& child : resolvedNode->Children()) {
    std::cout << child->GetName() << std::endl;
}
```

### 使用 YPath
```cpp
// 使用 YPath 查询
auto ypath = TYPath("/path/to/table/@compression_codec");
auto result = cypressManager->ExecuteYPath(
    ypath,
    EYPathCommand::Get
);

// 复杂 YPath 操作
auto complexPath = TYPath("/tables/*/[@rows > 1000]");
auto results = cypressManager->ExecuteYPath(
    complexPath,
    EYPathCommand::List
);
```

### 访问控制
```cpp
// 设置 ACL
auto acl = New<TAccessControlEntry>();
acl->Action = ESecurityAction::Allow;
acl->Subjects = {userId};
acl->Permissions = {EPermission::Read, EPermission::Write};

node->SetAcl({acl});

// 检查权限
auto allowed = securityManager->CheckPermission(
    user,
    node,
    EPermission::Write
);
```

## 配置参数

### Cypress Manager 配置
```yaml
cypress_manager:
  enable_versioning: true
  max_node_depth: 100
  max_children_per_node: 10000
  lock_manager:
    enable_deadlock_detection: true
    deadlock_detection_timeout: 30s
    max_locks_per_transaction: 10000

node_factory:
  default_type: map_node
  preserve_creation_time: true
  preserve_modification_time: true
  pessimistic_quota_check: true
```

### 访问控制配置
```yaml
access_control:
  enable_inheritance: true
  max_acl_size: 100
  audit_log_enabled: true
  default_permissions:
    - read
    - write

expiration:
  enabled: true
  cleanup_period: 1h
  batch_size: 1000
```

### 性能配置
```yaml
performance:
  enable_caching: true
  cache_size: 100MB
  batch_operation_size: 1000
  async_operations: true
  max_concurrent_operations: 100
```

## 实现原理

### 节点存储
- **内存存储**: 活跃节点存储在内存中
- **持久化**: 通过 Hydra 框架持久化
- **分片**: 大规模时分片存储
- **缓存**: 多级缓存优化访问

### 事务处理
- **MVCC**: 多版本并发控制
- **锁管理**: 细粒度的锁管理
- **死锁检测**: 实时死锁检测和预防
- **隔离级别**: 快照隔离保证

### YPath 实现
- **语法解析**: 解析 YPath 语法
- **路径匹配**: 高效的模式匹配
- **批量操作**: 批量执行优化
- **索引支持**: 索引加速查询

### 版本控制
- **写时复制**: Copy-on-Write 优化
- **增量存储**: 只存储差异
- **压缩**: 历史版本压缩
- **清理策略**: 智能版本清理

## 性能优化

### 内存优化
- **对象池**: 复用节点对象
- **压缩存储**: 压缩节点数据
- **延迟加载**: 按需加载节点
- **垃圾回收**: 及时回收无用对象

### 并发优化
- **读写锁**: 读写分离的锁机制
- **无锁数据结构**: 热点路径无锁化
- **细粒度锁**: 减少锁争用
- **异步处理**: 异步执行非关键操作

### I/O 优化
- **批量操作**: 批量减少 I/O
- **预取**: 预取相关数据
- **缓存**: 多级缓存系统
- **压缩**: 网络和存储压缩

## 监控和调试

### 关键指标
- 节点总数和类型分布
- 事务数量和执行时间
- 锁争用和死锁统计
- YPath 查询性能

### 调试命令
```bash
# 查看节点信息
yt get //path/to/node

# 查看事务
yt get //sys/transactions

# 查看锁
yt get //sys/locks

# YPath 查询
yt select "//tables/[@row_count > 1000]/{name, @row_count}"
```

### 性能分析
```bash
# 分析节点访问模式
yt get //sys/cypress_node_access_stats

# 查看锁信息
yt get //sys/locks/@info

# 分析事务
yt get //sys/transactions/@statistics
```

## 故障处理

### 常见问题
1. **节点不存在**: 检查路径和事务状态
2. **锁冲突**: 优化事务和锁顺序
3. **权限拒绝**: 检查 ACL 配置
4. **超时**: 调整操作批量大小

### 恢复机制
- **自动恢复**: 大部分问题自动处理
- **手动干预**: 复杂情况手动处理
- **数据恢复**: 从快照恢复
- **重建索引**: 重建损坏的索引

## 扩展性设计

### 水平扩展
- **分片**: 按路径分片
- **分布式事务**: 跨分片事务
- **负载均衡**: 智能负载分配
- **一致性保证**: 分布式一致性

### 垂直扩展
- **内存优化**: 减少内存占用
- **CPU 优化**: 提高 CPU 效率
- **并行处理**: 并行执行操作
- **异步优化**: 异步化处理

## 安全考虑

### 数据安全
- **访问控制**: 细粒度权限控制
- **审计日志**: 完整操作审计
- **数据加密**: 可选的加密存储
- **备份恢复**: 定期备份和恢复

### 运行时安全
- **输入验证**: 严格的输入验证
- **资源限制**: 防止资源耗尽
- **错误处理**: 安全的错误信息
- **日志脱敏**: 敏感信息脱敏

## 相关文档
- [Cypress 设计文档](../../../docs/cypress-design.md)
- [YPath 语言指南](../../../docs/ypath-language.md)
- [事务管理文档](../../../docs/transactions.md)