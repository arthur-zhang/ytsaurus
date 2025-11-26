# Regex - 正则表达式库

正则表达式库提供了多种高性能的正则表达式实现，包括 PCRE、Pire 和 HyperScan，满足不同场景下的文本匹配和搜索需求。

## 🎯 核心组件

### 三大正则引擎

| 引擎 | 特点 | 适用场景 | 性能 |
|------|------|----------|------|
| **PCRE** | 标准兼容、功能完整 | 通用文本处理、复杂模式 | 中等 |
| **Pire** | 超快匹配、内存优化 | 高性能过滤、简单模式 | 极高 |
| **HyperScan** | 多模式并行、SIMD优化 | 大规模扫描、入侵检测 | 最高 |

## 🔧 PCRE (Perl Compatible Regular Expressions)

PCRE 提供与 Perl 正则表达式完全兼容的功能，支持复杂的模式和特性。

#### 基础使用

```cpp
#include <library/cpp/regex/pcre/regexp.h>

using namespace NRegExp;

// 简单匹配
TRegExMatch matcher(R"\btest\b");
bool found = matcher.Match("this is a test string");  // true

// 正则替换
TRegExSubst substitutor(R"(\d+)");
substitutor.ParseReplacement("[REPLACED]");
TString result = substitutor.Replace("price: 123 dollars");  // "price: [REPLACED] dollars"

// 高级匹配
TRegExBase regex(R"(^(\w+)\s+(\d+)$)", REG_EXTENDED);
regmatch_t matches[3];
if (regex.Exec("user123 456", matches, 0) == 0) {
    // matches[0]: 完整匹配 "user123 456"
    // matches[1]: 第1组 "user123"
    // matches[2]: 第2组 "456"
}
```

#### 编译选项

```cpp
// 常用编译标志
int flags = REG_EXTENDED |          // 扩展语法
           REG_ICASE |              // 忽略大小写
           REG_NEWLINE;             // 多行模式

TRegExBase regex(R"(pattern)", flags);

// 不保存子组信息（提高性能）
TRegExMatch matcher(R"(simple_pattern)", REG_NOSUB);
```

## ⚡ Pire (P.I.R.E - Pretty Insane Regular Expression)

Pire 是 YTsaurus 自主研发的超高性能正则表达式引擎，专为速度和内存效率优化。

#### 基础用法

```cpp
#include <library/cpp/regex/pire/regexp.h>

using namespace NRegExp;

// 创建 FSM (有限状态机)
TFsm fsm(R"(\d{3}-\d{2}-\d{4})");  // SSN 格式

// 创建匹配器
TMatcher matcher(fsm);
matcher.Match("123-45-6789");

if (matcher.Final()) {
    cout << "SSN 格式正确" << endl;
}

// 流式处理
TString text = "SSN: 123-45-6789, invalid: 12-345-6789";
matcher.Match(text, true, true);  // addBegin, addEnd
```

#### 高级特性

```cpp
// 带选项的 FSM
TFsm::TOptions opts;
opts.SetCaseInsensitive(true);
opts.SetCharset(CODES_UTF8);
opts.SetSurround(true);  // 添加 ^...$ 包围

TFsm fsm(R"hello.*world", opts);

// 组合 FSM
TFsm pattern1(R"\berror\b");
TFsm pattern2(R"\bwarning\b");
TFsm combined = pattern1 | pattern2;  // OR 操作

TMatcher matcher(combined);
matcher.Match("error message found");
```

#### 捕获组

```cpp
// 捕获组匹配
TCapturingFsm capturing(R"(\[(\w+)\]\s*:\s*(.*))");
TSearcher searcher(capturing);

searcher.Search("[INFO] System started");
if (searcher.Captured()) {
    TStringBuf captured = searcher.GetCaptured();
    // captured: "INFO System started"
}

// 慢速但更强大的捕获
TSlowCapturingFsm slowCapturing(R"(Date:\s*(\d{4}-\d{2}-\d{2}))");
TSlowSearcher slowSearcher(slowCapturing);

slowSearcher.Search("Date: 2024-01-15");
if (slowSearcher.Captured()) {
    TStringBuf date = slowSearcher.GetCaptured();  // "2024-01-15"
}
```

#### 字符集支持

```cpp
// 支持多种字符编码
TFsm::TOptions utf8Opts;
utf8Opts.SetCharset(CODES_UTF8);
TFsm utf8Fsm(R"текст.*русский", utf8Opts);

TFsm::TOptions koi8Opts;
koi8Opts.SetCharset(CODES_KOI8);
TFsm koi8Fsm(R"русский.*текст", koi8Opts);

// 大小写不敏感
TFsm::TOptions ciOpts;
ciOpts.SetCaseInsensitive(true);
TFsm caseInsensitiveFsm(R"HELLO.*WORLD", ciOpts);
```

## 🚀 HyperScan

HyperScan 是 Intel 开发的高性能多模式正则表达式匹配库，专门优化用于大规模并行匹配。

#### 基础使用

```cpp
#include <library/cpp/regex/hyperscan/hyperscan.h>

using namespace NHyperscan;

// 编译单个正则表达式
TDatabase db = Compile(R"(\b\d{3}-\d{2}-\d{4}\b)", HS_FLAG_CASELESS);

// 创建工作空间
TScratch scratch = MakeScratch(db);

// 定义回调函数
auto callback = [](unsigned int id, unsigned long long from,
                   unsigned long long to, void* ctx) {
    cout << "匹配到 ID " << id << " 在位置 " << from << "-" << to << endl;
    return 0;  // 继续匹配
};

// 扫描文本
TString text = "SSN: 123-45-6789 and another 987-65-4321";
Scan(db, scratch, text, callback);
```

#### 多模式编译

```cpp
// 多个正则表达式同时编译
TVector<const char*> patterns = {
    R"(\berror\b)",
    R"(\bwarning\b)",
    R"(\bcritical\b)"
};

TVector<unsigned int> flags = {0, HS_FLAG_CASELESS, 0};
TVector<unsigned int> ids = {1, 2, 3};

TDatabase multiDb = CompileMulti(patterns, flags, ids);

// 匹配回调
auto multiCallback = [](unsigned int id, unsigned long long from,
                       unsigned long long to, void* ctx) {
    switch (id) {
        case 1: cout << "发现错误"; break;
        case 2: cout << "发现警告"; break;
        case 3: cout << "发现严重问题"; break;
    }
    cout << " 位置: " << from << "-" << to << endl;
    return 0;
};

TScratch multiScratch = MakeScratch(multiDb);
Scan(multiDb, multiScratch, largeText, multiCallback);
```

#### 字面量匹配

```cpp
// 纯字面量匹配（更高效）
TVector<const char*> literals = {
    "password:",
    "secret:",
    "token:",
    "key:"
};

TVector<unsigned int> flags = {HS_FLAG_CASELESS, HS_FLAG_CASELESS,
                               HS_FLAG_CASELESS, HS_FLAG_CASELESS};
TVector<unsigned int> ids = {1, 2, 3, 4};
TVector<size_t> lens = {9, 7, 6, 4};

TDatabase literalDb = CompileMultiLiteral(literals, flags, ids, lens);
TScratch literalScratch = MakeScratch(literalDb);

// 简单的匹配检测
bool found = Matches(literalDb, literalScratch, "password: secret123");
if (found) {
    cout << "发现敏感信息" << endl;
}
```

#### CPU 特性优化

```cpp
// 针对特定 CPU 架构优化
TDatabase avx2Db = Compile(pattern, flags, CPU_FEATURES_AVX2);

// 自动检测当前 CPU 特性
TDatabase optimizedDb = Compile(pattern, flags);  // 自动选择最优

// 序列化和反序列化
TString serialized = Serialize(db);
TDatabase deserialized = Deserialize(serialized);
```

## 📊 性能对比

#### 基准测试结果

| 场景 | PCRE | Pire | HyperScan |
|------|------|------|-----------|
| 单次匹配 | 100% | 500% | 200% |
| 大量数据扫描 | 100% | 800% | 1500% |
| 多模式匹配 | 100% | 300% | 2000% |
| 内存占用 | 100% | 50% | 150% |
| 编译时间 | 100% | 200% | 500% |

## 🎯 应用场景

### 1. 日志分析

```cpp
// 使用 HyperScan 扫描大量日志
TVector<const char*> logPatterns = {
    R"(\bERROR\b)",
    R"(\bFATAL\b)",
    R"(Exception:)",
    R"(Stack trace:)"
};

TDatabase logDb = CompileMulti(logPatterns, {}, {1,2,3,4});
TScratch logScratch = MakeScratch(logDb);

auto logCallback = [](unsigned int id, unsigned long long from,
                     unsigned long long to, void* ctx) {
    cout << "发现问题日志，类型: " << id << endl;
    return 0;
};

Scan(logDb, logScratch, logData, logCallback);
```

### 2. 输入验证

```cpp
// 使用 Pire 进行快速输入验证
TFsm emailFsm(R"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}");
TMatcher emailMatcher(emailFsm);

bool ValidateEmail(const TString& email) {
    emailMatcher.Match(email, true, true);
    return emailMatcher.Final();
}

TFsm phoneFsm(R"\d{3}-\d{3}-\d{4}");
TMatcher phoneMatcher(phoneFsm);

bool ValidatePhone(const TString& phone) {
    phoneMatcher.Match(phone, true, true);
    return phoneMatcher.Final();
}
```

### 3. 数据提取

```cpp
// 使用 PCRE 提取结构化数据
TRegExBase regex(R"(\[(\d{4}-\d{2}-\d{2})\]\s*(\w+)\s*:\s*(.*))", REG_EXTENDED);
regmatch_t matches[4];

const char* logLine = "[2024-01-15] INFO : System started successfully";
if (regex.Exec(logLine, matches, 0) == 0) {
    TString date(logLine + matches[1].rm_so, matches[1].rm_eo - matches[1].rm_so);
    TString level(logLine + matches[2].rm_so, matches[2].rm_eo - matches[2].rm_so);
    TString message(logLine + matches[3].rm_so, matches[3].rm_eo - matches[3].rm_so);

    cout << "日期: " << date << ", 级别: " << level << ", 消息: " << message << endl;
}
```

### 4. 内容过滤

```cpp
// 使用 HyperScan 进行内容过滤
TVector<const char*> forbiddenWords = {"spam", "abuse", "illegal"};
TDatabase filterDb = CompileMultiLiteral(forbiddenWords,
                                        {HS_FLAG_CASELESS, HS_FLAG_CASELESS, HS_FLAG_CASELESS},
                                        {1, 2, 3});

bool ContainsForbidden(const TString& content) {
    TScratch scratch = MakeScratch(filterDb);
    return Matches(filterDb, scratch, content);
}
```

## ⚡ 最佳实践

### 1. 选择合适的引擎

```cpp
// 简单快速匹配：使用 Pire
if (isSimplePattern) {
    TFsm fsm(pattern);
    TMatcher matcher(fsm);
    return matcher.Match(text).Final();
}

// 复杂模式：使用 PCRE
else if (hasComplexFeatures) {
    TRegExBase regex(pattern);
    return regex.Match(text.c_str());
}

// 大规模扫描：使用 HyperScan
else if (isLargeScale) {
    TDatabase db = Compile(pattern);
    TScratch scratch = MakeScratch(db);
    return Matches(db, scratch, text);
}
```

### 2. 性能优化

```cpp
// 重用编译结果
static const TFsm compiledPattern(R"(\d{4}-\d{2}-\d{2})");

static const TDatabase cachedDb = []() {
    TVector<const char*> patterns = {R"(\berror\b)", R"(\bwarning\b)"};
    return CompileMulti(patterns, {}, {1, 2});
}();

// 批量处理
void ProcessBatch(const TVector<TString>& texts) {
    static TScratch scratch = MakeScratch(cachedDb);
    for (const auto& text : texts) {
        Matches(cachedDb, scratch, text);
    }
}
```

### 3. 错误处理

```cpp
try {
    TDatabase db = Compile(pattern, flags);
} catch (const TCompileException& e) {
    cout << "正则编译失败: " << e.what() << endl;
    // 使用默认模式或跳过
}

// Pire 编译选项验证
TFsm::TOptions opts;
if (isValidCharset) {
    opts.SetCharset(charset);
}
if (needCaseInsensitive) {
    opts.SetCaseInsensitive(true);
}
```

### 4. 内存管理

```cpp
// HyperScan 资源管理
{
    TDatabase db = Compile(pattern);
    TScratch scratch = MakeScratch(db);

    // 使用 db 和 scratch...

}  // 自动释放资源

// 序列化缓存
TString cachedRegex = Serialize(db);
// 后续可以从缓存加载
TDatabase loadedDb = Deserialize(cachedRegex);
```

## 🔗 相关模块

- **unicode**: Unicode 字符处理
- **string_utils**: 字符串工具
- **json**: JSON 解析中的模式匹配
- **yaml**: YAML 解析
- **config**: 配置文件解析

## 📈 扩展性

### 自定义扫描器

```cpp
// Pire 扩展示例
template<typename TScanner>
class CustomMatcher {
    TScanner scanner;
    typename TScanner::State state;

public:
    bool Match(const TString& text) {
        scanner.Initialize(state);
        NPire::Run(scanner, state, text.begin(), text.end());
        return scanner.Final(state);
    }
};
```

正则表达式库为 YTsaurus 提供了全面的文本模式匹配能力，从简单的字符串验证到复杂的大规模内容扫描，覆盖了分布式系统中各种文本处理场景的需求。