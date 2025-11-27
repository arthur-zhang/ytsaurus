# Java 客户端库

YTsaurus 的 Java 客户端库，提供完整的 Java 语言接口，用于与 YTsaurus 分布式存储和计算平台进行交互。

## 目录结构

### 核心客户端库

- **ytsaurus-client/** - 主客户端模块
  - 完整的 Java 客户端实现
  - 提供表操作、文件操作、MapReduce 接口
  - 事务管理和分布式锁支持

- **ytsaurus-client-core/** - 核心功能模块
  - 客户端核心功能
  - 网络通信和协议处理
  - 连接池和会话管理

- **ytsaurus-testlib/** - 测试库
  - 单元测试和集成测试支持
  - 模拟服务和测试工具

### 数据序列化

- **yson/** - YSON 序列化库
  - YSON 格式的 Java 实现
  - 高效的编码和解码
  - 与其他语言客户端兼容

- **yson-tree/** - YSON 树结构
  - YSON 数据的树形表示
  - 便于数据操作和转换
  - 支持 JSON 转换

- **yson-json-converter/** - JSON 转换器
  - YSON 与 JSON 格式互转
  - RESTful API 支持
  - 数据导入导出工具

- **skiff/** - Skiff 格式支持
  - 高性能列式存储格式
  - 数据交换优化
  - 大规模数据处理

### 工具库

- **annotations/** - 注解支持
  - 自定义注解定义
  - 代码生成和验证
  - 配置管理

- **type-info/** - 类型信息
  - 运行时类型信息
  - 类型转换和验证
  - 泛型支持

### 示例和文档

- **ytsaurus-client-examples/** - 示例代码
  - 丰富的使用示例
  - 最佳实践演示
  - 完整的应用示例

### 构建配置

- **ya.make** - 构建配置
  - YaTool 构建系统配置
  - 依赖管理

## 功能特性

### 核心功能
- **数据访问**：完整支持表的 CRUD 操作
- **文件系统**：文件上传、下载、管理
- **分布式计算**：MapReduce、运行操作
- **事务支持**：ACID 事务和 MVCC
- **并发控制**：分布式锁和乐观锁

### 高级特性
- **批量操作**：高效的批量读写
- **流式处理**：大数据流式处理
- **缓存机制**：智能缓存优化
- **连接池**：高性能连接管理
- **故障恢复**：自动重试和故障转移

### 性能优化
- **压缩传输**：多种压缩算法
- **并行处理**：多线程并发
- **内存管理**：零拷贝优化
- **网络优化**：连接复用

## 使用方法

### Maven 依赖
```xml
<dependency>
    <groupId>tech.ytsaurus</groupId>
    <artifactId>ytsaurus-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 基本使用示例
```java
import tech.ytsaurus.client.*;
import tech.ytsaurus.client.operations.*;

public class YtsaurusExample {
    public static void main(String[] args) {
        // 创建客户端
        try (YtClient yt = YtClient.builder()
                .setCluster("localhost")
                .setToken("your-token")
                .build()) {

            // 读取表
            List<Row> rows = yt.readTable("//tmp/my_table")
                    .as(Row.class)
                    .collect(Collectors.toList());

            System.out.println("Read " + rows.size() + " rows");

            // 写入表
            yt.writeTable("//tmp/output", rows);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### MapReduce 示例
```java
import tech.ytsaurus.client.operations.*;
import tech.ytsaurus.client.operations.MapReduce;

public class MapReduceExample {
    public void runMapReduce(YtClient yt) {
        // 定义 Map 函数
        Mapper mapper = new Mapper() {
            @Override
            public void map(Row input, RowWriter writer) {
                // Map 逻辑
                String key = input.get("key");
                Long value = input.get("value");
                writer.add(Row.builder()
                        .set("key", key)
                        .set("value", value * 2)
                        .build());
            }
        };

        // 定义 Reduce 函数
        Reducer reducer = new Reducer() {
            @Override
            public void reduce(Row key, Iterable<Row> rows, RowWriter writer) {
                // Reduce 逻辑
                Long sum = 0;
                for (Row row : rows) {
                    sum += row.get("value");
                }
                writer.add(Row.builder()
                        .set("key", key.get("key"))
                        .set("sum", sum)
                        .build());
            }
        };

        // 执行 MapReduce
        MapReduceSpec spec = MapReduceSpec.builder()
                .addInput("//tmp/input")
                .addOutput("//tmp/output")
                .mapper(mapper)
                .reducer(reducer)
                .build();

        Operation operation = yt.mapReduce(spec);
        operation.join();
    }
}
```

### 事务使用示例
```java
public void transactionExample(YtClient yt) {
    try (Transaction tx = yt.startTransaction()) {
        // 在事务中执行操作
        tx.createTable("//tmp/new_table", TableSpec.builder().build());
        tx.writeTable("//tmp/new_table", data);

        // 提交事务
        tx.commit();
    } catch (Exception e) {
        // 事务会自动回滚
        e.printStackTrace();
    }
}
```

## 性能调优

### 连接配置
```java
YtClient yt = YtClient.builder()
        .setCluster("localhost")
        .setMaxConnections(100)
        .setConnectionTimeout(Duration.ofSeconds(30))
        .setRequestTimeout(Duration.ofMinutes(5))
        .build();
```

### 批量操作优化
```java
// 使用批量读取
BatchRead batch = yt.createBatchRead();
batch.addTable("//tmp/table1");
batch.addTable("//tmp/table2");
Map<String, List<Row>> results = batch.read();

// 使用批量写入
BatchWrite batch = yt.createBatchWrite();
batch.addTable("//tmp/output1", data1);
batch.addTable("//tmp/output2", data2);
batch.write();
```

## 依赖项

- Java 8+
- Maven/Gradle (构建工具)
- YTsaurus 集群 (运行环境)
- 可选：Spring Boot (集成支持)

## 最佳实践

1. **资源管理**
   - 使用 try-with-resources 管理客户端
   - 及时释放资源和连接
   - 避免创建过多客户端实例

2. **错误处理**
   - 捕获和处理所有异常
   - 实现适当的重试机制
   - 记录详细的错误日志

3. **性能优化**
   - 使用批量操作
   - 合理设置超时时间
   - 利用连接池

4. **事务管理**
   - 保持事务简短
   - 避免长时间持有锁
   - 正确处理事务冲突