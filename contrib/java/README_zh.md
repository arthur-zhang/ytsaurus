# Java 第三方库集合

本目录包含 YTsaurus 项目依赖的 Java 第三方库和相关源码。这些库按照标准 Java 包结构组织，提供了 Java 生态系统的集成能力。

## 目录结构

### 核心包结构

#### **antlr/** - ANTLR 解析器生成器
- ANTLR（ANother Tool for Language Recognition）
- 语法分析器生成器
- 用于语言解析和处理

#### **javax/** - Java 扩展包
- Java 标准扩展
- 企业级 Java API
- JEE 相关组件

#### **org/** - 组织包
- Apache 项目
- Google 库
- 其他开源项目

#### **com/** - 商业包
- 第三方商业库
- 专有软件包

#### **io/** - 输入输出包
- 网络库
- 序列化框架
- 数据处理工具

#### **net/** - 网络包
- 网络协议实现
- 客户端库
- 通信框架

#### **junit/** - 测试框架
- JUnit 单元测试框架
- 测试运行器
- 断言工具

#### **pl/** - 可能包含 Polish 相关包

## 主要组件

### 解析器工具
- **ANTLR** - 强大的解析器生成器
  - 支持多种语言目标
  - 语法定义和词法分析
  - 抽象语法树（AST）生成

### 测试框架
- **JUnit** - Java 单元测试标准
  - 测试注解支持
  - 断言方法
  - 测试套件管理

### 可能包含的库

#### Apache 项目
- **Commons Lang** - Java 基础工具扩展
- **Commons IO** - 输入输出工具
- **Commons Collections** - 集合框架扩展
- **HttpClient** - HTTP 客户端库
- **Maven** - 项目管理工具

#### 数据处理
- **Jackson** - JSON 处理库
- **Gson** - Google JSON 库
- **Protobuf** - Protocol Buffers Java 版
- **Avro** - 数据序列化系统

#### 网络和通信
- **Netty** - 异步网络框架
- **gRPC** - RPC 框架
- **OkHttp** - HTTP 客户端

#### 日志框架
- **SLF4J** - 简单日志门面
- **Logback** - 日志实现
- **Log4j2** - Apache 日志框架

## 使用方法

### Maven 集成
```xml
<!-- 在 pom.xml 中添加依赖 -->
<dependencies>
    <dependency>
        <groupId>org.antlr</groupId>
        <artifactId>antlr4-runtime</artifactId>
        <version>4.9.2</version>
    </dependency>

    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### Gradle 集成
```gradle
dependencies {
    implementation 'org.antlr:antlr4-runtime:4.9.2'
    testImplementation 'junit:junit:4.13.2'
}
```

### 使用 ANTLR
```java
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;

// 解析输入
CharStream input = CharStreams.fromString("input text");
MyGrammarLexer lexer = new MyGrammarLexer(input);
CommonTokenStream tokens = new CommonTokenStream(lexer);
MyGrammarParser parser = new MyGrammarParser(tokens);

// 构建语法树
ParseTree tree = parser.ruleName();

// 遍历语法树
ParseTreeWalker walker = new ParseTreeWalker();
MyListener listener = new MyListener();
walker.walk(listener, tree);
```

### 使用 JUnit
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
import org.junit.After;

public class MyTest {
    @Before
    public void setUp() {
        // 测试前准备
    }

    @Test
    public void testSomething() {
        // 测试逻辑
        int result = calculate(2, 3);
        Assert.assertEquals(5, result);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testException() {
        // 测试异常
        calculate(-1, 0);
    }

    @After
    public void tearDown() {
        // 测试后清理
    }
}
```

## 构建配置

### 编译设置
```xml
<!-- Maven 编译插件 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.8.1</version>
    <configuration>
        <source>11</source>
        <target>11</target>
    </configuration>
</plugin>
```

### ANTLR 插件
```xml
<!-- ANTLR Maven 插件 -->
<plugin>
    <groupId>org.antlr</groupId>
    <artifactId>antlr4-maven-plugin</artifactId>
    <version>4.9.2</version>
    <executions>
        <execution>
            <goals>
                <goal>antlr4</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## 版本管理

### Java 版本支持
- Java 8 LTS
- Java 11 LTS（推荐）
- Java 17 LTS

### 库版本策略
- 使用稳定版本
- 保持向后兼容
- 定期更新安全补丁

## 最佳实践

### 依赖管理
1. **使用依赖管理工具**
   - Maven 依赖管理
   - Gradle 依赖配置
   - 版本范围定义

2. **避免依赖冲突**
   - 使用 dependencyManagement
   - 排除冲突依赖
   - 版本统一管理

### 测试策略
```java
// 参数化测试
@RunWith(Parameterized.class)
public class ParameterizedTest {
    @Parameters
    public static Collection<Object[]> data() {
        return Arrays.asList(new Object[][] {
            {1, 1, 2},
            {2, 3, 5},
            {3, 5, 8}
        });
    }

    private int a, b, expected;

    public ParameterizedTest(int a, int b, int expected) {
        this.a = a;
        this.b = b;
        this.expected = expected;
    }

    @Test
    public void testAdd() {
        Assert.assertEquals(expected, add(a, b));
    }
}
```

## 性能优化

### JVM 调优
```bash
# JVM 参数
-Xms2g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+PrintGCDetails
```

### 代码优化
- 使用 StringBuilder 代替字符串拼接
- 合理使用集合类
- 对象池和缓存
- 并发编程最佳实践

## 安全考虑

### 依赖安全
- 定期更新依赖
- 检查漏洞报告
- 使用 OWASP Dependency Check

### 代码安全
- 输入验证
- SQL 注入防护
- XSS 防护
- 加密敏感数据

## 调试和诊断

### 日志配置
```xml
<!-- logback.xml -->
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT" />
    </root>
</configuration>
```

### 调试工具
- JVisualVM
- JConsole
- YourKit
- Java Mission Control

## CI/CD 集成

### Maven 构建
```yaml
# GitHub Actions
name: Java CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'temurin'
    - name: Build with Maven
      run: mvn clean install
```

## 维护指南

### 添加新库
1. 评估许可证
2. 检查兼容性
3. 更新构建文件
4. 添加测试
5. 更新文档

### 版本升级
1. 检查 release notes
2. 运行兼容性测试
3. 更新版本号
4. 提交变更

## 资源链接

- [Maven 中央仓库](https://search.maven.org/)
- [JUnit 官方网站](https://junit.org/)
- [ANTLR 官方网站](https://www.antlr.org/)
- [Oracle Java 文档](https://docs.oracle.com/en/java/)