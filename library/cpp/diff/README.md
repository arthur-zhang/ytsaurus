# diff 文本差异分析模块

[diff](.) 是 YTsaurus 中专门用于计算和分析文本差异的高性能 C++ 库。该模块基于最长公共子序列（LCS）算法，能够高效地识别和展示两个文本序列之间的差异，支持字符级别和单词级别的差异分析。

## 📋 项目描述

`diff` 模块提供了一套完整的文本差异分析解决方案，能够以结构化的方式展示两个文本或数据序列之间的差异。它采用了基于 LCS（最长公共子序列）的高效算法，特别适合用于版本控制、数据同步、变更检测等场景。

### 核心特性

- **高效算法**：基于 O(r log n) 时间复杂度的 LCS 算法
- **灵活模式**：支持字符级和词级差异分析
- **结构化输出**：提供清晰的差异块结构
- **可定制格式**：支持自定义差异展示格式
- **内存优化**：O(r) 额外内存使用，r 为匹配对数量

## ⚠️ 性能注意事项

底层算法 `library/cpp/lcs` 的时间复杂度为 **O(r log n)**，额外内存使用为 **O(r)**，其中 r 是满足 S1[i] = S2[j] 的 (i, j) 对数量。

**重要性能特征**：
- 当比较文件与自身（或仅有微小修改的文件）时，复杂度会退化为关于最频繁行出现次数的二次方
- 对于高度重复的文本，性能可能显著下降
- 建议在处理大型重复文件时使用适当的分块策略

## 🚀 核心特性

### 1. 差异块结构

模块使用 `TChunk<T>` 结构来表示差异块：

```cpp
template <typename T>
struct TChunk {
    TConstArrayRef<T> Left;    // 左侧序列中的差异部分
    TConstArrayRef<T> Right;   // 右侧序列中的差异部分
    TConstArrayRef<T> Common;  // 双方序列中的公共部分
};
```

### 2. 双模式支持

- **字符级差异**：逐字符比较，适合精确的文本差异分析
- **词级差异**：基于分隔符的单词比较，适合自然语言处理

### 3. 多语言支持

- **ASCII 字符**：`char` 类型，支持标准文本
- **Unicode 字符**：`wchar16` 类型，支持宽字符和国际化文本

## 🏗️ 主要组件

### 核心函数

#### 通用差异分析函数
```cpp
template <typename T>
size_t InlineDiff(TVector<TChunk<T>>& chunks,
                  const TConstArrayRef<T>& left,
                  const TConstArrayRef<T>& right);
```

#### 字符串特化版本
```cpp
// ASCII 字符串差异
size_t InlineDiff(TVector<TChunk<char>>& chunks,
                  const TStringBuf& left,
                  const TStringBuf& right,
                  const TString& delims = TString());

// Unicode 字符串差异
size_t InlineDiff(TVector<TChunk<wchar16>>& chunks,
                  const TWtringBuf& left,
                  const TWtringBuf& right,
                  const TUtf16String& delims = TUtf16String());
```

#### 差异块打印函数
```cpp
template <typename TFormatter, typename T>
void PrintChunks(IOutputStream& out,
                 const TFormatter& fmt,
                 const TVector<TChunk<T>>& chunks);
```

## 💡 使用示例

### 基础字符级差异分析

```cpp
#include <library/cpp/diff/diff.h>
#include <util/stream/str.h>

// 简单字符级差异
TVector<TChunk<char>> chunks;
TString text1 = "hello world";
TString text2 = "hello there world";

size_t distance = InlineDiff(chunks, text1, text2);

// 输出结果
TStringStream output;
PrintChunks(output, formatter, chunks);
Cout << "差异距离: " << distance << Endl;
Cout << "差异详情: " << output.Str() << Endl;
```

### 词级差异分析

```cpp
// 基于空格分隔符的词级差异
TVector<TChunk<char>> chunks;
TString text1 = "The quick brown fox jumps over the lazy dog";
TString text2 = "The fast brown cat jumps over the sleeping dog";

size_t distance = InlineDiff(chunks, text1, text2, " \t\n");

// 处理差异块
for (const auto& chunk : chunks) {
    if (!chunk.Left.empty() || !chunk.Right.empty()) {
        Cout << "删除: " << TString(chunk.Left.begin(), chunk.Left.size()) << Endl;
        Cout << "添加: " << TString(chunk.Right.begin(), chunk.Right.size()) << Endl;
    }
    if (!chunk.Common.empty()) {
        Cout << "公共: " << TString(chunk.Common.begin(), chunk.Common.size()) << Endl;
    }
}
```

### 自定义格式化器

```cpp
struct MyFormatter {
    TStringBuf Special(const TStringBuf& str) const {
        return TStringBuf("[") + str + TStringBuf("]");
    }

    TStringBuf Left(const TConstArrayRef<char>& str) const {
        return TStringBuf("-") + TStringBuf(str.begin(), str.size());
    }

    TStringBuf Right(const TConstArrayRef<char>& str) const {
        return TStringBuf("+") + TStringBuf(str.begin(), str.size());
    }

    TStringBuf Common(const TConstArrayRef<char>& str) const {
        return TStringBuf(str.begin(), str.size());
    }
};

// 使用自定义格式化器
TStringStream output;
PrintChunks(output, MyFormatter(), chunks);
Cout << "自定义格式: " << output.Str() << Endl;
```

### Unicode 文本差异分析

```cpp
// Unicode 文本差异分析
TVector<TChunk<wchar16>> chunks;
TUtf16String text1 = u"你好世界";
TUtf16String text2 = u"你好中国";
TUtf16String delims = u" \t\n";

size_t distance = InlineDiff(chunks, text1, text2, delims);

// 处理 Unicode 差异块
for (const auto& chunk : chunks) {
    if (!chunk.Common.empty()) {
        TUtf16String common(chunk.Common.begin(), chunk.Common.size());
        Cout << "公共部分: " << common << Endl;
    }
}
```

### 高级差异分析模式

```cpp
// 实现类似 git diff 的功能
class GitLikeFormatter {
public:
    GitLikeFormatter(IOutputStream& out) : Out(out) {}

    void Process(const TVector<TChunk<char>>& chunks) {
        int lineNum = 1;

        for (const auto& chunk : chunks) {
            // 处理删除的行
            for (const auto& line : SplitLines(chunk.Left)) {
                Out << "-" << lineNum << ": " << line << "\n";
                lineNum++;
            }

            // 处理添加的行
            for (const auto& line : SplitLines(chunk.Right)) {
                Out << "+" << lineNum << ": " << line << "\n";
                lineNum++;
            }

            // 处理公共行
            for (const auto& line : SplitLines(chunk.Common)) {
                Out << " " << lineNum << ": " << line << "\n";
                lineNum++;
            }
        }
    }

private:
    IOutputStream& Out;

    TVector<TString> SplitLines(const TConstArrayRef<char>& text) {
        // 实现行分割逻辑
        TVector<TString> lines;
        // ... 分割实现
        return lines;
    }
};
```

## 🎯 应用场景

### 1. 版本控制系统
- 文件变更检测和可视化
- 代码审查工具
- 合并冲突解决辅助

### 2. 内容管理系统
- 文档修订历史追踪
- 变更记录生成
- 审核流程支持

### 3. 数据同步工具
- 数据库记录差异比较
- 配置文件同步
- 备份验证

### 4. 质量保证
- 测试结果比较
- 输出验证
- 回归测试

### 5. 自然语言处理
- 文本相似度分析
- 机器翻译质量评估
- 内容去重

## ⚡ 最佳实践

### 1. 性能优化

#### 分块处理大型文件
```cpp
class FileDiffProcessor {
public:
    void ProcessLargeFile(const TString& file1, const TString& file2) {
        constexpr size_t CHUNK_SIZE = 1024 * 1024; // 1MB chunks

        TFileInput in1(file1), in2(file2);
        TString buf1, buf2;

        while (!in1.Exhausted() && !in2.Exhausted()) {
            buf1 = in1.Read(CHUNK_SIZE);
            buf2 = in2.Read(CHUNK_SIZE);

            ProcessChunk(buf1, buf2);
        }
    }

private:
    void ProcessChunk(const TString& chunk1, const TString& chunk2) {
        TVector<TChunk<char>> chunks;
        InlineDiff(chunks, chunk1, chunk2);
        // 处理差异块...
    }
};
```

#### 缓存和复用
```cpp
class DiffCache {
public:
    size_t GetCachedDiff(const TString& key1, const TString& key2,
                        TVector<TChunk<char>>& chunks) {
        auto cacheKey = MakeCacheKey(key1, key2);

        if (auto it = Cache.find(cacheKey); it != Cache.end()) {
            chunks = it->second.Chunks;
            return it->second.Distance;
        }

        size_t distance = InlineDiff(chunks, key1, key2);
        Cache[cacheKey] = {chunks, distance};

        return distance;
    }

private:
    struct CacheEntry {
        TVector<TChunk<char>> Chunks;
        size_t Distance;
    };

    THashMap<ui64, CacheEntry> Cache;
};
```

### 2. 内存管理

#### 使用 ArrayRef 避免数据拷贝
```cpp
// 优化的差异分析函数
void AnalyzeDiffWithMinCopy(const TString& text1, const TString& text2) {
    // 使用 ArrayRef 避免字符串拷贝
    TConstArrayRef<char> ref1(text1.data(), text1.size());
    TConstArrayRef<char> ref2(text2.data(), text2.size());

    TVector<TChunk<char>> chunks;
    InlineDiff(chunks, ref1, ref2);

    // 处理差异时仍然避免不必要的拷贝
    for (const auto& chunk : chunks) {
        ProcessChunkWithoutCopy(chunk);
    }
}
```

### 3. 错误处理和验证

```cpp
class SafeDiffProcessor {
public:
    bool ProcessDiff(const TString& text1, const TString& text2,
                    TVector<TChunk<char>>& chunks) {
        try {
            // 输入验证
            if (!ValidateInput(text1, text2)) {
                return false;
            }

            // 大小限制检查
            if (text1.size() > MAX_SIZE || text2.size() > MAX_SIZE) {
                Cerr << "输入文本过大，超过限制: " << MAX_SIZE << Endl;
                return false;
            }

            // 执行差异分析
            size_t distance = InlineDiff(chunks, text1, text2);

            // 结果验证
            return ValidateResult(text1, text2, chunks, distance);

        } catch (const std::exception& e) {
            Cerr << "差异分析异常: " << e.what() << Endl;
            return false;
        }
    }

private:
    static constexpr size_t MAX_SIZE = 100 * 1024 * 1024; // 100MB

    bool ValidateInput(const TString& text1, const TString& text2) {
        // 实现输入验证逻辑
        return true;
    }

    bool ValidateResult(const TString& text1, const TString& text2,
                       const TVector<TChunk<char>>& chunks, size_t distance) {
        // 验证差异结果的正确性
        return true;
    }
};
```

### 4. 多线程处理

```cpp
class ParallelDiffProcessor {
public:
    std::future<size_t> ProcessDiffAsync(const TString& text1, const TString& text2) {
        return std::async(std::launch::async, [this, text1, text2]() {
            TVector<TChunk<char>> chunks;
            return InlineDiff(chunks, text1, text2);
        });
    }

    void ProcessBatch(const std::vector<std::pair<TString, TString>>& pairs) {
        std::vector<std::future<size_t>> futures;

        for (const auto& [text1, text2] : pairs) {
            futures.push_back(ProcessDiffAsync(text1, text2));
        }

        // 等待所有任务完成
        for (auto& future : futures) {
            future.wait();
        }
    }
};
```

## 🔗 相关模块

- **library/cpp/lcs**：底层最长公共子序列算法实现
- **util/string/split**：字符串分割工具
- **util/generic/array_ref**：数组引用工具，用于零拷贝操作
- **util/stream/output**：输出流处理

## 📝 注意事项

1. **性能考虑**：对于高度重复的文本，算法性能可能显著下降
2. **内存使用**：大型文本的差分分析可能消耗大量内存
3. **编码处理**：确保使用正确的字符编码处理多语言文本
4. **线程安全**：当前的实现不是线程安全的，多线程环境需要额外同步
5. **错误处理**：在处理大型或异常输入时需要适当的错误处理机制

## 🔮 扩展建议

1. **算法优化**：考虑实现更高效的差异算法，如 Myers 算法
2. **格式支持**：添加对更多文件格式的原生支持
3. **可视化工具**：开发配套的差异可视化组件
4. **并行化**：实现并行差异分析以提高大型文件的处理性能
5. **增量分析**：支持增量差异分析以提高效率

`diff` 模块为 YTsaurus 项目提供了强大而灵活的文本差异分析能力，是构建版本控制、内容管理和数据同步工具的重要基础组件。
