# YTsaurus Cell Master 客户端

## 概述

`cell_master_client` 目录提供了 YTsaurus Cell Master 的客户端接口定义。该模块定义了 Master Cell 的各种角色和功能类型，为客户端与 Master Cell 的交互提供基础支持。

## 核心功能

### Master Cell 角色定义
定义了 YTsaurus Master Cell 可以承担的各种角色：
- **Cypress 节点宿主**: 管理 Cypress 元数据树
- **事务协调器**: 协调分布式事务
- **Chunk 宿主**: 管理 Chunk 元数据
- **专用 Chunk 宿主**: 专门负责 Chunk 管理的 Master
- **扩展事务协调器**: 扩展的事务协调功能
- **Sequoia 节点宿主**: 支持 Sequoia 存储引擎

### 角色枚举系统
提供了两种枚举类型来表示 Master Cell 角色：
- **EMasterCellRoles**: 位掩码枚举，支持多角色组合
- **EMasterCellRole**: 单一角色枚举

## 主要文件说明

### 公共接口定义
- `public.h`: 公共类型和枚举定义
  - `EMasterCellRoles`: 位掩码角色枚举
  - `EMasterCellRole`: 单一角色枚举
  - Proto 命名空间声明

## Master Cell 角色详解

### 角色类型定义

#### EMasterCellRoles（位掩码枚举）
```cpp
DEFINE_BIT_ENUM(EMasterCellRoles,
    ((None)                      (0x0000))           // 无角色
    ((CypressNodeHost)           (0x0001))           // Cypress 节点宿主
    ((TransactionCoordinator)    (0x0002))           // 事务协调器
    ((ChunkHost)                 (0x0004))           // Chunk 宿主
    ((DedicatedChunkHost)        (0x0008))           // 专用 Chunk 宿主
    ((ExTransactionCoordinator)  (0x0010))           // 扩展事务协调器
    ((SequoiaNodeHost)           (0x0020))           // Sequoia 节点宿主
);
```

#### EMasterCellRole（单一角色枚举）
```cpp
DEFINE_ENUM(EMasterCellRole,
    ((Unknown)                   (0x0000))           // 未知角色
    ((CypressNodeHost)           (0x0001))           // Cypress 节点宿主
    ((TransactionCoordinator)    (0x0002))           // 事务协调器
    ((ChunkHost)                 (0x0004))           // Chunk 宿主
    ((DedicatedChunkHost)        (0x0008))           // 专用 Chunk 宿主
    ((ExTransactionCoordinator)  (0x0010))           // 扩展事务协调器
    ((SequoiaNodeHost)           (0x0020))           // Sequoia 节点宿主
);
```

### 角色功能说明

#### CypressNodeHost (Cypress 节点宿主)
- **功能**: 管理 Cypress 元数据树
- **职责**:
  - 文件系统层次结构管理
  - 节点创建、删除、修改
  - 权限控制和访问管理
- **重要性**: 核心角色，负责集群的元数据管理

#### TransactionCoordinator (事务协调器)
- **功能**: 协调分布式事务
- **职责**:
  - 事务状态管理
  - 两阶段提交协调
  - 事务超时和清理
- **重要性**: 保证数据一致性的关键组件

#### ChunkHost (Chunk 宿主)
- **功能**: 管理 Chunk 元数据
- **职责**:
  - Chunk 位置信息管理
  - Chunk 副本策略控制
  - Chunk 生命周期管理
- **重要性**: 数据存储管理的核心

#### DedicatedChunkHost (专用 Chunk 宿主)
- **功能**: 专门负责 Chunk 管理的 Master
- **职责**:
  - 专注于 Chunk 元数据管理
  - 提供高性能 Chunk 操作
  - 独立的 Chunk 服务
- **使用场景**: 大规模数据存储集群

#### ExTransactionCoordinator (扩展事务协调器)
- **功能**: 扩展的事务协调功能
- **职责**:
  - 高级事务特性支持
  - 复杂事务场景处理
  - 性能优化的协调算法
- **使用场景**: 复杂业务场景

#### SequoiaNodeHost (Sequoia 节点宿主)
- **功能**: 支持 Sequoia 存储引擎
- **职责**:
  - Sequoia 元数据管理
  - 多集群协调
  - 分布式一致性保证
- **重要性**: 多集群统一管理的关键

## 使用示例

### 角色检查
```cpp
#include <yt/yt/client/cell_master_client/public.h>

using namespace NYT::NCellMasterClient;

// 检查 Master 是否具有特定角色
EMasterCellRoles roles = EMasterCellRoles::CypressNodeHost |
                        EMasterCellRoles::TransactionCoordinator;

if (roles & EMasterCellRoles::CypressNodeHost) {
    // 处理 Cypress 相关操作
}

if (roles & EMasterCellRoles::TransactionCoordinator) {
    // 处理事务相关操作
}
```

### 角色转换
```cpp
// 从单一角色转换为位掩码角色
EMasterCellRole singleRole = EMasterCellRole::CypressNodeHost;
EMasterCellRoles bitMaskRole = static_cast<EMasterCellRoles>(singleRole);

// 检查角色是否为未知类型
if (singleRole == EMasterCellRole::Unknown) {
    // 处理未知角色情况
}
```

### 多角色组合
```cpp
// 组合多个角色
EMasterCellRoles combinedRoles = EMasterCellRoles::CypressNodeHost |
                                 EMasterCellRoles::TransactionCoordinator |
                                 EMasterCellRoles::ChunkHost;

// 检查是否同时具有多个角色
bool hasAllRoles = (combinedRoles & (EMasterCellRoles::CypressNodeHost |
                                     EMasterCellRoles::TransactionCoordinator)) ==
                   (EMasterCellRoles::CypressNodeHost | EMasterCellRoles::TransactionCoordinator);
```

## 设计原则

### 枚举一致性
- `EMasterCellRoles` 和 `EMasterCellRole` 的枚举值保持一致
- 确保两种枚举类型可以安全转换
- 新增角色时需要同步更新两个枚举

### 位操作优化
- `EMasterCellRoles` 支持位运算操作
- 可以高效地组合和检查多个角色
- 使用位掩码提高存储和计算效率

### 向后兼容性
- 保持现有枚举值不变
- 新增角色采用高位赋值
- 提供 Unknown 值处理未知情况

## 扩展性

### 新角色添加
当需要添加新的 Master Cell 角色时：
1. 在两个枚举中同时添加新角色
2. 确保枚举值的一致性
3. 使用适当的位掩码值
4. 更新相关文档和注释

### 角色组合
- 支持灵活的角色组合
- 允许一个 Master Cell 承担多个角色
- 根据集群规模和需求动态配置

## 注意事项

1. **枚举同步**: 确保两个枚举类型始终保持同步
2. **位操作**: 正确使用位运算操作符
3. **类型安全**: 注意枚举类型之间的转换
4. **兼容性**: 新增角色时考虑向后兼容性
5. **文档维护**: 及时更新角色说明和使用文档

## 相关模块

该模块与以下模块紧密相关：
- `object_client`: 对象管理客户端
- `cypress_client`: Cypress 客户端
- `transaction_client`: 事务客户端
- `chunk_client`: Chunk 客户端
- `sequoia_client`: Sequoia 客户端

## 最佳实践

1. **角色检查**: 使用位运算进行高效的角色检查
2. **类型转换**: 谨慎处理枚举类型之间的转换
3. **错误处理**: 妥善处理未知角色情况
4. **性能考虑**: 在性能敏感场景下使用位掩码操作
5. **代码可读性**: 使用有意义的变量名和注释