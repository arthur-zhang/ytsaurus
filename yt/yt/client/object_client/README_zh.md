# Object Client - 对象客户端

本模块提供 YTsaurus 中对象的标识、类型定义和操作功能。对象是 YTsaurus 的核心概念，包括文件、表、事务、Chunk、用户、账号等各种实体。

## 核心概念

### 1. 对象标识符 (TObjectId)

YTsaurus 中的每个对象都有一个全局唯一的 128 位标识符：

```cpp
using TObjectId = TGuid;  // 128位全局唯一标识符
```

ObjectId 结构：
- **Part 0** (32位)：熵值，用于随机化
- **Part 1** (32位)：低16位是对象类型，高16位是Cell ID
- **Part 2** (32位)：64位计数器的低32位
- **Part 3** (32位)：64位计数器的高32位

### 2. 对象类型 (EObjectType)

YTsaurus 支持多种对象类型，主要分为：

#### 非版本化对象
- **事务管理器**：
  - `Transaction` - 事务
  - `AtomicTabletTransaction` - 原子Tablet事务
  - `NonAtomicTabletTransaction` - 非原子Tablet事务
  - `NestedTransaction` - 嵌套事务
  - `ExternalizedTransaction` - 外部化事务
  - `UploadTransaction` - 上传事务
  - `SystemTransaction` - 系统事务

- **Chunk管理器**：
  - `Chunk` - 数据块
  - `ErasureChunk` - 纠删码Chunk
  - `ErasureChunkPart_0` 到 `ErasureChunkPart_15` - 纠删码Chunk的16个部分
  - `JournalChunk` - 日志Chunk
  - `ErasureJournalChunk` - 纠删码日志Chunk
  - `ErasureJournalChunkPart_0` 到 `ErasureJournalChunkPart_15` - 纠删码日志Chunk部分
  - `ChunkList` - Chunk列表
  - `ChunkView` - Chunk视图
  - `Artifact` - 工件
  - `ChunkLocation` - Chunk位置
  - `NbdChunk` - NBD Chunk

#### 版本化对象 (Cypress节点)
- **静态节点**：
  - `StringNode` - 字符串节点
  - `Int64Node` - 64位整数节点
  - `Uint64Node` - 64位无符号整数节点
  - `DoubleNode` - 双精度浮点节点
  - `MapNode` - 映射节点
  - `BooleanNode` - 布尔节点
  - `DeprecatedListNode` - 已弃用列表节点

- **动态节点**：
  - `File` - 文件
  - `Table` - 表
  - `Journal` - 日志
  - `Orchid` - Orchid（监控树）
  - `Link` - 链接
  - `Document` - 文档
  - `ReplicatedTable` - 复制表
  - `ReplicationLogTable` - 复制日志表

- **安全对象**：
  - `Account` - 账号
  - `User` - 用户
  - `Group` - 组
  - `NetworkProject` - 网络项目
  - `AccessControlObject` - 访问控制对象
  - `AccessControlObjectNamespace` - 访问控制对象命名空间

#### 特殊对象
- **Sequoia节点**：
  - `SequoiaMapNode` - Sequoia映射节点
  - `SequoiaLink` - Sequoia链接

- **门户对象**：
  - `PortalEntrance` - 门户入口
  - `PortalExit` - 门户出口

- **嫁接对象**：
  - `Rootstock` - 砧木
  - `Scion` - 接穗

- **Tablet相关**：
  - `TabletCell` - Tablet单元
  - `Tablet` - Tablet
  - `SortedDynamicTabletStore` - 有序动态Tablet存储

### 3. Cell标签 (TCellTag)

```cpp
using TCellTag = ui16;  // 16位Cell标签
constexpr auto MinValidCellTag = 0x0001;
constexpr auto MaxValidCellTag = 0xf000;
constexpr auto PrimaryMasterCellTagSentinel = 0xf003;
constexpr auto NotReplicatedCellTagSentinel = 0xf001;
constexpr auto InvalidCellTag = 0xf004;
```

## 使用示例

### 创建和使用对象ID
```cpp
#include <yt/yt/client/object_client/helpers.h>

// 创建随机对象ID
auto objectId = MakeRandomId(EObjectType::Table, PrimaryMasterCellTagSentinel);

// 创建常规对象ID
auto regularId = MakeRegularId(
    EObjectType::File,
    PrimaryMasterCellTagSentinel,
    NHydra::TVersion{1, 100},  // segment, revision
    0x12345678  // entropy
);

// 创建Sequoia对象ID
auto sequoiaId = MakeSequoiaId(
    EObjectType::SequoiaMapNode,
    0x0001,
    NTransactionClient::TTimestamp{1234567890000000},  // timestamp
    0x87654321  // entropy
);

// 创建知名对象ID
auto wellKnownId = MakeWellKnownId(
    EObjectType::Master,
    PrimaryMasterCellTagSentinel,
    0x8000000000000000  // counter with high bit set
);

// 从ID提取信息
auto type = TypeFromId(objectId);
auto cellTag = CellTagFromId(objectId);
auto counter = CounterFromId(objectId);
auto entropy = EntropyFromId(objectId);
auto version = VersionFromId(objectId);

// 检查特殊ID类型
bool isWellKnown = IsWellKnownId(objectId);
bool isSequoia = IsSequoiaId(objectId);
```

### 对象类型检查
```cpp
#include <yt/yt/client/object_client/helpers.h>

EObjectType type = EObjectType::Table;

// 类型检查
bool isVersioned = IsVersionedType(type);           // true - 表是版本化的
bool isUser = IsUserType(type);                     // true - 用户可以创建表
bool isSchemaful = IsSchemafulType(type);           // true - 表可以有schema
bool isTable = IsTableType(type);                   // true
bool isTabletOwner = IsTabletOwnerType(type);       // true - 表可以拥有tablet
bool isChunkOwner = IsChunkOwnerType(type);         // true - 表可以拥有chunk
bool isComposite = IsCompositeNodeType(type);       // true - 表可以包含子节点

// 事务类型检查
bool isCypressTx = IsCypressTransactionType(EObjectType::Transaction);
bool isSystemTx = IsSystemTransactionType(EObjectType::SystemTransaction);
bool isUploadTx = IsUploadTransactionType(EObjectType::UploadTransaction);
bool isExternalized = IsExternalizedTransactionType(EObjectType::ExternalizedTransaction);

// 特殊对象检查
bool isReplicated = IsReplicatedTableType(EObjectType::ReplicatedTable);
bool isCell = IsCellType(EObjectType::TabletCell);
bool isMedium = IsMediumType(EObjectType::DomesticMedium);
bool isCollocation = IsCollocationType(EObjectType::TableCollocation);
```

### Schema相关操作
```cpp
#include <yt/yt/client/object_client/helpers.h>

// Schema类型操作
EObjectType regularType = EObjectType::Table;
bool hasSchema = HasSchema(regularType);  // true

EObjectType schemaType = SchemaTypeFromType(regularType);  // MasterTableSchema
EObjectType backType = TypeFromSchemaType(schemaType);    // Table

// 创建Schema对象ID
auto schemaId = MakeSchemaObjectId(EObjectType::Table, PrimaryMasterCellTagSentinel);
```

### YPath转换
```cpp
#include <yt/yt/client/object_client/helpers.h>

// 从对象ID创建YPath
TObjectId objectId = MakeRandomId(EObjectType::File, PrimaryMasterCellTagSentinel);
NYPath::TYPath objectPath = FromObjectId(objectId);  // "#1-2-3-4"

// 格式化对象类型
std::string typeStr = FormatObjectType(EObjectType::Table);  // "table"
std::string schemaStr = FormatObjectType(EObjectType::MasterTableSchema);  // "schema"
```

## 设计原理

### 对象ID设计
1. **全局唯一性**：128位ID确保全球范围内不冲突
2. **类型嵌入**：类型信息嵌入ID中，便于快速判断
3. **Cell分区**：Cell标签支持多Cell集群
4. **时间戳支持**：Sequoia对象使用时间戳代替版本号

### 版本化对象
1. **Cypress集成**：版本化对象是Cypress树的一部分
2. **多版本支持**：保留对象的历史版本
3. **ACID事务**：支持ACID事务语义
4. **锁机制**：细粒度锁支持并发访问

### 特殊对象支持
1. **知名对象**：单例系统对象使用特殊标记
2. **Sequoia支持**：新一代分布式存储系统
3. **门户和嫁接**：支持对象在不同位置之间的映射

## 错误处理

```cpp
DEFINE_ERROR_ENUM(
    (PrerequisiteCheckFailed,                  1000),  // 前提条件检查失败
    (InvalidObjectLifeStage,                  1001),  // 无效对象生命周期
    (CrossCellAdditionalPath,                 1002),  // 跨Cell额外路径
    (CrossCellRevisionPrerequisitePath,       1003),  // 跨Cell版本前提路径
    (ForwardedRequestFailed,                  1004),  // 转发请求失败
    (CannotCacheMutatingRequest,              1005),  // 无法缓存修改请求
    (InvalidObjectType,                       1006),  // 无效对象类型
    (RequestInvolvesSequoia,                  1007),  // 请求涉及Sequoia
    (RequestInvolvesCypress,                  1008),  // 请求涉及Cypress
    (BeginCopyDeprecated,                     1009),  // Copy操作已弃用
    (PrerequisitePathDifferFromExecutionPaths,1010),  // 前提路径与执行路径不同
);
```

## 依赖项

- `yt/yt/client/election/public.h` - 选举系统
- `yt/yt/client/job_tracker_client/public.h` - 任务跟踪
- `yt/yt/client/hydra/version.h` - Hydra版本
- `yt/yt/client/transaction_client/public.h` - 事务客户端
- `yt/yt/client/ypath/public.h` - YPath操作
- `yt/yt/core/rpc/public.h` - RPC通信
- `library/cpp/yt/misc/guid.h` - GUID操作
- `library/cpp/yt/misc/enum.h` - 枚举支持
- `library/cpp/yt/misc/hash.h` - 哈希支持

## 注意事项

1. **ID生成**：对象ID应由系统生成，不要手动构造
2. **Cell标签**：正确设置Cell标签，确保对象在正确的Cell中
3. **类型一致性**：对象类型必须与其用途匹配
4. **版本化**：Cypress节点会自动版本化，非版本化对象不会
5. **特殊对象**：知名对象和Sequoia对象有特殊的创建规则
6. **事务作用域**：某些对象必须在事务中创建

## 相关模块

- `yt/yt/server/master/object_server` - 对象服务端实现
- `yt/yt/server/master/cypress_server` - Cypress服务端实现
- `yt/yt/client/tablet_client` - Tablet客户端
- `yt/yt/client/transaction_client` - 事务客户端