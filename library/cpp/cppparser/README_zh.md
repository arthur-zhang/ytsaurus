# C++ Parser C++代码解析器

## 项目描述

CppParser 是 YTsaurus 中的轻量级 C++ 代码词法分析器，提供快速的 C++ 源代码解析能力。该解析器专注于词法分析，不进行语义检查，采用类似 SAX 解析器的事件驱动接口设计，能够高效地处理大型 C++ 代码库。

通过流式处理和事件回调机制，该解析器能够以最小的内存占用处理任意大小的源文件，非常适合代码分析工具、文档生成器和代码质量检查等应用场景。

## 核心特性

### ⚡ 高性能解析
- **流式处理**: 支持流式输入，内存占用最小化
- **词法分析**: 专注于词法级别分析，处理速度快
- **事件驱动**: 基于 SAX 模式的事件回调机制
- **零拷贝**: 高效的数据传递和处理

### 🔧 丰富的事件类型
- **代码分析**: 识别代码块、语句、表达式
- **字符串处理**: 正确处理字符串字面量和字符常量
- **注释识别**: 支持单行和多行注释
- **预处理器**: 处理预处理器指令

### 📊 详细解析
- **关键字识别**: 识别 C++ 关键字
- **数字字面量**: 支持十进制、八进制、十六进制和浮点数
- **标识符分析**: 分离标识符和关键字
- **语法元素**: 识别各种语法符号和操作符

### 🎯 灵活接口
- **分层设计**: 提供简单和完整两种解析器
- **可扩展**: 支持自定义关键字集合
- **位置信息**: 提供详细的字符位置信息
- **易于集成**: 简单的接口设计

## 架构设计

### 1. 核心组件

#### 解析器基础 (TCppSaxParser)
```cpp
class TCppSaxParser: public IOutputStream {
public:
    // 文本信息结构
    struct TText {
        TText();
        TText(ui64 offset);
        TText(const TString& data, ui64 offset);

        void Reset() noexcept;

        TString Data;    // 文本内容
        ui64 Offset;     // 字符偏移位置
    };

    // 工作器接口
    class TWorker {
    public:
        virtual ~TWorker();

        // 生命周期事件
        virtual void DoStart() = 0;
        virtual void DoEnd() = 0;

        // 内容事件
        virtual void DoString(const TText& text) = 0;
        virtual void DoCharacter(const TText& text) = 0;
        virtual void DoCode(const TText& text) = 0;
        virtual void DoOneLineComment(const TText& text) = 0;
        virtual void DoMultiLineComment(const TText& text) = 0;
        virtual void DoPreprocessor(const TText& text) = 0;
    };

    TCppSaxParser(TWorker* worker);
    ~TCppSaxParser() override;
};
```

#### 简单解析器 (TCppSimpleSax)
```cpp
class TCppSimpleSax: public TCppSaxParser::TWorker {
public:
    // 基础事件
    void DoStart() override = 0;
    void DoEnd() override = 0;
    void DoString(const TText& text) override = 0;
    void DoCharacter(const TText& text) override = 0;

    // 扩展事件
    virtual void DoWhiteSpace(const TText& text) = 0;
    virtual void DoIdentifier(const TText& text) = 0;
    virtual void DoSyntax(const TText& text) = 0;

    // 继承的基础事件
    void DoOneLineComment(const TText& text) override = 0;
    void DoMultiLineComment(const TText& text) override = 0;
    void DoPreprocessor(const TText& text) override = 0;

private:
    void DoCode(const TText& text) override;
};
```

#### 完整解析器 (TCppFullSax)
```cpp
class TCppFullSax: public TCppSimpleSax {
public:
    // 详细事件处理
    void DoKeyword(const TText& text);         // C++ 关键字
    void DoName(const TText& text);            // 标识符名称
    void DoOctNumber(const TText& text);       // 八进制数字
    void DoHexNumber(const TText& text);       // 十六进制数字
    void DoDecNumber(const TText& text);       // 十进制数字
    void DoFloatNumber(const TText& text);     // 浮点数字

    // 重写的基类事件
    void DoStart() override;
    void DoEnd() override;
    void DoString(const TText& text) override;
    void DoCharacter(const TText& text) override;
    void DoWhiteSpace(const TText& text) override;
    void DoSyntax(const TText& text) override;
    void DoOneLineComment(const TText& text) override;
    void DoMultiLineComment(const TText& text) override;
    void DoPreprocessor(const TText& text) override;

    // 关键字管理
    void AddKeyword(const TString& keyword);
};
```

### 2. 解析状态机

#### 词法分析状态
```cpp
enum EState {
    Code,                    // 普通代码
    CommentBegin,            // 注释开始
    String,                  // 字符串字面量
    Character,               // 字符字面量
    OneLineComment,          // 单行注释
    MultiLineComment,        // 多行注释
    MultiLineCommentEnd,     // 多行注释结束
    Preprocessor            // 预处理器指令
};
```

#### 状态转换逻辑
```cpp
class TCppSaxParser::TImpl {
private:
    EState State_ = Code;           // 当前状态
    TText Text_;                    // 当前文本缓冲
    TWorker* Worker_;              // 工作器指针
    bool SkipNext_ = false;         // 跳过下一个字符
    ui64 Line_ = 0;                // 当前行号
    ui64 Column_ = 0;              // 当前列号

    void ProcessInput(const char* data, size_t len);
    void HandleCharacter(char ch);
    void HandleStringStart();
    void HandleCommentStart();
    void HandlePreprocessor();
};
```

## 使用示例

### 1. 基本解析使用
```cpp
#include <library/cpp/cppparser/parser.h>

class SimpleCodeAnalyzer: public TCppSimpleSax {
public:
    void DoStart() override {
        Cout << "开始解析 C++ 代码" << Endl;
        LineCount_ = 0;
        CommentLines_ = 0;
        CodeLines_ = 0;
    }

    void DoEnd() override {
        Cout << "解析完成:" << Endl;
        Cout << "  总行数: " << LineCount_ << Endl;
        Cout << "  代码行数: " << CodeLines_ << Endl;
        Cout << "  注释行数: " << CommentLines_ << Endl;
    }

    void DoString(const TText& text) override {
        Cout << "字符串: " << text.Data << " (位置: " << text.Offset << ")" << Endl;
    }

    void DoCharacter(const TText& text) override {
        Cout << "字符常量: " << text.Data << Endl;
    }

    void DoWhiteSpace(const TText& text) override {
        // 处理空白字符（包括换行）
        for (char ch : text.Data) {
            if (ch == '\n') {
                LineCount_++;
            }
        }
    }

    void DoIdentifier(const TText& text) override {
        Cout << "标识符: " << text.Data << Endl;
    }

    void DoSyntax(const TText& text) override {
        Cout << "语法符号: " << text.Data << Endl;
    }

    void DoOneLineComment(const TText& text) override {
        Cout << "单行注释: " << text.Data << Endl;
        CommentLines_++;
    }

    void DoMultiLineComment(const TText& text) override {
        Cout << "多行注释: " << text.Data << Endl;
        // 统计多行注释中的行数
        CommentLines_ += std::count(text.Data.begin(), text.Data.end(), '\n') + 1;
    }

    void DoPreprocessor(const TText& text) override {
        Cout << "预处理器: " << text.Data << Endl;
    }

private:
    size_t LineCount_ = 0;
    size_t CommentLines_ = 0;
    size_t CodeLines_ = 0;
};

void AnalyzeCppFile(const TString& filename) {
    TFileInput file(filename);
    SimpleCodeAnalyzer analyzer;
    TCppSaxParser parser(&analyzer);

    // 流式处理文件内容
    char buffer[4096];
    while (!file.Read(buffer, sizeof(buffer)).empty()) {
        parser.Write(buffer, sizeof(buffer));
    }
    parser.Finish();
}
```

### 2. 代码统计工具
```cpp
class CodeStatisticsAnalyzer: public TCppFullSax {
private:
    struct Statistics {
        size_t totalLines = 0;
        size_t codeLines = 0;
        size_t commentLines = 0;
        size_t blankLines = 0;
        size_t functions = 0;
        size_t classes = 0;
        size_t keywords = 0;
        size_t identifiers = 0;
        size_t stringLiterals = 0;
        size_t numberLiterals = 0;
    };

    Statistics stats_;

public:
    void DoStart() override {
        stats_ = Statistics{};
    }

    void DoEnd() override {
        Cout << "=== C++ 代码统计报告 ===" << Endl;
        Cout << "总行数: " << stats_.totalLines << Endl;
        Cout << "代码行数: " << stats_.codeLines << Endl;
        Cout << "注释行数: " << stats_.commentLines << Endl;
        Cout << "空白行数: " << stats_.blankLines << Endl;
        Cout << "函数数量: " << stats_.functions << Endl;
        Cout << "类数量: " << stats_.classes << Endl;
        Cout << "关键字数量: " << stats_.keywords << Endl;
        Cout << "标识符数量: " << stats_.identifiers << Endl;
        Cout << "字符串字面量: " << stats_.stringLiterals << Endl;
        Cout << "数字字面量: " << stats_.numberLiterals << Endl;
    }

    void DoWhiteSpace(const TText& text) override {
        for (char ch : text.Data) {
            if (ch == '\n') {
                stats_.totalLines++;
            }
        }
    }

    void DoKeyword(const TText& text) override {
        stats_.keywords++;

        // 统计特定的关键字
        if (text.Data == "class") {
            stats_.classes++;
        }
    }

    void DoName(const TText& text) override {
        stats_.identifiers++;
    }

    void DoOctNumber(const TText& text) override {
        stats_.numberLiterals++;
    }

    void DoHexNumber(const TText& text) override {
        stats_.numberLiterals++;
    }

    void DoDecNumber(const TText& text) override {
        stats_.numberLiterals++;
    }

    void DoFloatNumber(const TText& text) override {
        stats_.numberLiterals++;
    }

    void DoString(const TText& text) override {
        stats_.stringLiterals++;
    }

    void DoOneLineComment(const TText& text) override {
        stats_.commentLines++;
    }

    void DoMultiLineComment(const TText& text) override {
        stats_.commentLines += std::count(text.Data.begin(), text.Data.end(), '\n') + 1;
    }
};
```

### 3. 代码格式化器
```cpp
class CodeFormatter: public TCppSimpleSax {
private:
    TStringOutput output_;
    int indentLevel_ = 0;
    bool needIndent_ = true;
    bool atLineStart_ = true;

    void WriteIndent() {
        if (needIndent_ && !atLineStart_) {
            for (int i = 0; i < indentLevel_; ++i) {
                output_ << "    ";
            }
            needIndent_ = false;
        }
    }

public:
    CodeFormatter(const TString& outputPath)
        : output_(outputPath) {}

    void DoStart() override {
        indentLevel_ = 0;
        needIndent_ = true;
        atLineStart_ = true;
    }

    void DoEnd() override {
        output_.Finish();
    }

    void DoString(const TText& text) override {
        WriteIndent();
        output_ << text.Data;
        atLineStart_ = false;
    }

    void DoCharacter(const TText& text) override {
        WriteIndent();
        output_ << text.Data;
        atLineStart_ = false;
    }

    void DoWhiteSpace(const TText& text) override {
        for (char ch : text.Data) {
            if (ch == '\n') {
                output_ << ch;
                needIndent_ = true;
                atLineStart_ = true;
            } else if (ch != ' ' || !needIndent_) {
                output_ << ch;
            }
        }
    }

    void DoIdentifier(const TText& text) override {
        WriteIndent();
        output_ << text.Data;
        atLineStart_ = false;
    }

    void DoSyntax(const TText& text) override {
        WriteIndent();

        // 处理特殊语法符号
        if (text.Data == "{") {
            output_ << "{\n";
            indentLevel_++;
            needIndent_ = true;
            atLineStart_ = true;
        } else if (text.Data == "}") {
            output_ << "}\n";
            if (indentLevel_ > 0) {
                indentLevel_--;
            }
            needIndent_ = true;
            atLineStart_ = true;
        } else if (text.Data == ";") {
            output_ << ";\n";
            needIndent_ = true;
            atLineStart_ = true;
        } else {
            output_ << text.Data;
            atLineStart_ = false;
        }
    }

    void DoOneLineComment(const TText& text) override {
        WriteIndent();
        output_ << text.Data << "\n";
        needIndent_ = true;
        atLineStart_ = true;
    }

    void DoMultiLineComment(const TText& text) override {
        WriteIndent();
        output_ << text.Data;
        if (text.Data.back() != '\n') {
            output_ << "\n";
        }
        needIndent_ = true;
        atLineStart_ = true;
    }

    void DoPreprocessor(const TText& text) override {
        WriteIndent();
        output_ << text.Data << "\n";
        needIndent_ = true;
        atLineStart_ = true;
    }
};
```

### 4. 符号提取器
```cpp
class SymbolExtractor: public TCppFullSax {
private:
    struct SymbolInfo {
        TString name;
        TString type;      // function, class, variable, etc.
        size_t line;
        size_t offset;
    };

    TVector<SymbolInfo> symbols_;

public:
    void DoStart() override {
        symbols_.clear();
    }

    void DoEnd() override {
        Cout << "=== 提取的符号 ===" << Endl;
        for (const auto& symbol : symbols_) {
            Cout << symbol.type << ": " << symbol.name
                 << " (行: " << symbol.line << ", 位置: " << symbol.offset << ")" << Endl;
        }
    }

    void DoKeyword(const TText& text) override {
        // 根据上下文和关键字判断符号类型
        if (text.Data == "class") {
            nextSymbolType_ = "class";
        } else if (text.Data == "struct") {
            nextSymbolType_ = "struct";
        } else if (text.Data == "enum") {
            nextSymbolType_ = "enum";
        } else if (text.Data == "namespace") {
            nextSymbolType_ = "namespace";
        }
    }

    void DoName(const TText& text) override {
        if (!nextSymbolType_.empty()) {
            SymbolInfo symbol;
            symbol.name = text.Data;
            symbol.type = nextSymbolType_;
            symbol.line = currentLine_;
            symbol.offset = text.Offset;
            symbols_.push_back(symbol);

            nextSymbolType_.clear();
        }
    }

private:
    TString nextSymbolType_;
    size_t currentLine_ = 0;
};
```

## 应用场景

### 1. 代码质量检查
```cpp
class CodeQualityChecker: public TCppSimpleSax {
private:
    struct Issue {
        TString type;
        TString description;
        size_t line;
        size_t column;
    };

    TVector<Issue> issues_;

public:
    void DoStart() override {
        issues_.clear();
    }

    void DoEnd() override {
        for (const auto& issue : issues_) {
            Cout << issue.type << ": " << issue.description
                 << " (行: " << issue.line << ", 列: " << issue.column << ")" << Endl;
        }
    }

    void DoSyntax(const TText& text) override {
        // 检查特定的语法问题
        if (text.Data == "goto") {
            Issue issue;
            issue.type = "Warning";
            issue.description = "使用 goto 语句";
            issue.line = currentLine_;
            issue.column = currentColumn_;
            issues_.push_back(issue);
        }
    }

    void DoString(const TText& text) override {
        // 检查字符串长度
        if (text.Data.length() > 1000) {
            Issue issue;
            issue.type = "Warning";
            issue.description = "过长的字符串字面量";
            issue.line = currentLine_;
            issue.column = currentColumn_;
            issues_.push_back(issue);
        }
    }

private:
    size_t currentLine_ = 0;
    size_t currentColumn_ = 0;
};
```

### 2. 文档生成器
```cpp
class DocumentationGenerator: public TCppSimpleSax {
private:
    struct ClassInfo {
        TString name;
        TString comment;
        TVector<TString> methods;
    };

    TVector<ClassInfo> classes_;
    TString currentComment_;

public:
    void DoStart() override {
        classes_.clear();
        currentComment_.clear();
    }

    void DoEnd() override {
        // 生成 Markdown 文档
        Cout << "# API 文档" << Endl << Endl;

        for (const auto& cls : classes_) {
            Cout << "## " << cls.name << Endl << Endl;
            if (!cls.comment.empty()) {
                Cout << cls.comment << Endl << Endl;
            }

            if (!cls.methods.empty()) {
                Cout << "### 方法" << Endl << Endl;
                for (const auto& method : cls.methods) {
                    Cout << "- " << method << Endl;
                }
                Cout << Endl;
            }
        }
    }

    void DoKeyword(const TText& text) override {
        if (text.Data == "class") {
            nextIsClassName_ = true;
        }
    }

    void DoName(const TText& text) override {
        if (nextIsClassName_) {
            ClassInfo info;
            info.name = text.Data;
            info.comment = currentComment_;
            classes_.push_back(info);

            nextIsClassName_ = false;
            currentComment_.clear();
        }
    }

    void DoOneLineComment(const TText& text) override {
        if (text.Data.StartsWith("///") || text.Data.StartsWith("/**")) {
            currentComment_ = text.Data;
        }
    }

private:
    bool nextIsClassName_ = false;
};
```

## 性能特性

### 处理效率
- **流式处理**: 支持处理任意大小的文件
- **内存效率**: 最小化内存占用，只需保存当前上下文
- **处理速度**: 高性能的字符处理算法
- **缓存友好**: 优化的内存访问模式

### 准确性
- **词法准确**: 严格遵循 C++ 词法规则
- **边界处理**: 正确处理字符串边界和转义序列
- **注释识别**: 准确识别嵌套注释和特殊情况
- **预处理器**: 正确处理预处理器指令

## 最佳实践

### 1. 错误处理
```cpp
class RobustParser: public TCppSimpleSax {
public:
    void DoStart() override {
        errorCount_ = 0;
        warningCount_ = 0;
    }

    void DoEnd() override {
        if (errorCount_ > 0) {
            Cout << "解析完成，发现 " << errorCount_ << " 个错误" << Endl;
        }
    }

protected:
    void ReportError(const TString& message, const TText& text) {
        Cout << "错误: " << message << " 在位置 " << text.Offset << Endl;
        errorCount_++;
    }

    void ReportWarning(const TString& message, const TText& text) {
        Cout << "警告: " << message << " 在位置 " << text.Offset << Endl;
        warningCount_++;
    }

private:
    size_t errorCount_ = 0;
    size_t warningCount_ = 0;
};
```

### 2. 内存优化
```cpp
class MemoryEfficientParser: public TCppSimpleSax {
private:
    TString buffer_;  // 复用的字符串缓冲区

public:
    void DoString(const TText& text) override {
        // 复用缓冲区避免频繁分配
        buffer_ = text.Data;
        ProcessString(buffer_);
    }

    void DoIdentifier(const TText& text) override {
        buffer_ = text.Data;
        ProcessIdentifier(buffer_);
    }

private:
    void ProcessString(const TString& str);
    void ProcessIdentifier(const TString& id);
};
```

### 3. 多文件处理
```cpp
class ProjectAnalyzer {
public:
    void AnalyzeProject(const TString& projectPath) {
        TVector<TString> cppFiles = FindCppFiles(projectPath);

        for (const auto& file : cppFiles) {
            Cout << "分析文件: " << file << Endl;
            AnalyzeFile(file);
        }
    }

private:
    void AnalyzeFile(const TString& filename) {
        try {
            TFileInput file(filename);
            MyAnalyzer analyzer;
            TCppSaxParser parser(&analyzer);

            char buffer[8192];
            while (!file.Read(buffer, sizeof(buffer)).empty()) {
                parser.Write(buffer, sizeof(buffer));
            }
            parser.Finish();
        } catch (const std::exception& e) {
            Cerr << "分析文件失败: " << filename << " - " << e.what() << Endl;
        }
    }

    TVector<TString> FindCppFiles(const TString& path);
};
```

## 限制和注意事项

### 功能限制
- **词法级别**: 只进行词法分析，不进行语义分析
- **标准依赖**: 依赖特定 C++ 标准的词法规则
- **编码支持**: 主要支持 UTF-8 编码的源文件

### 使用建议
- **合理缓冲**: 使用适当的缓冲区大小以平衡性能和内存
- **错误处理**: 实现适当的错误处理机制
- **资源管理**: 确保正确释放解析器资源

## 总结

CppParser C++ 代码解析器提供了一个高效、灵活的 C++ 源代码词法分析解决方案。通过流式处理和事件驱动的设计，该解析器能够以最小的资源消耗处理大型代码库。

无论是构建代码分析工具、文档生成器，还是实现代码质量检查系统，该解析器都能提供强大的基础支持。其简洁的接口和良好的扩展性使其成为各种 C++ 代码处理应用的理想选择。