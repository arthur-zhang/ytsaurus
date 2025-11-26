# XML 库

YTsaurus XML 处理库，提供高性能的 XML 文档解析、生成和操作功能。

## 📋 项目概述

XML 库为 YTsaurus 提供了完整的 XML（eXtensible Markup Language）处理能力，基于 libxml2 构建，提供了现代 C++ 接口，支持大型 XML 文档的流式处理和高效的 DOM 操作。

### 🎯 核心特性

- **高性能解析**: 基于 libxml2 的优化解析器
- **内存效率**: 支持大文件的流式处理
- **XPath 支持**: 完整的 XPath 1.0 查询支持
- **命名空间**: 完整的 XML 命名空间支持
- **验证**: XML Schema 和 DTD 验证
- **编码支持**: 多种字符编码支持
- **安全解析**: 防止 XXE 攻击的安全解析

## 🏗️ 架构设计

### 组件结构

```
XML Library
├── Document           # 文档处理
│   ├── TXmlDocument   # XML 文档类
│   ├── TXmlTextReader # 文本读取器
│   ├── TXmlNodeAttr   # 节点属性
│   └── TXmlOptions    # 解析选项
├── Init              # 初始化
│   └── libxml-guards  # 库初始化保护
├── Parser            # 解析器
│   ├── SAX Parser     # 事件驱动解析
│   └── DOM Parser     # 文档对象模型解析
└── Utilities         # 工具类
    ├── XPath          # XPath 查询
    └── Validation     # 验证工具
```

### 处理流程

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XML Input     │───▶│   Parser        │───▶│   DOM Tree      │
│   (File/String) │    │ (libxml2)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XPath Query   │◄───│   Navigation   │◄───│   Traversal     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Validation    │◄───│   Modification  │◄───│   Serialization │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💻 使用方法

### 基础 XML 解析

```cpp
#include <library/cpp/xml/document/xml-document.h>
#include <library/cpp/xml/document/xml-options.h>
#include <library/cpp/xml/init/init.h>
#include <util/stream/file.h>

void BasicXMLParsing() {
    // 初始化 XML 库
    NYXml::TInitializeGuard xmlGuard;

    // 示例 XML 内容
    TString xmlContent = R"(<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>C++ Programming</title>
        <author>John Smith</author>
        <price currency="USD">49.99</price>
        <categories>
            <category>Programming</category>
            <category>Computer Science</category>
        </categories>
    </book>
    <book id="2">
        <title>Design Patterns</title>
        <author>Erich Gamma</author>
        <price currency="USD">39.95</price>
        <categories>
            <category>Software Design</category>
            <category>Architecture</category>
        </categories>
    </book>
</catalog>
)";

    try {
        // 创建解析选项
        NYXml::TXmlOptions options;
        options.SetParseDTD(false);  // 不解析 DTD
        options.SetNoEntities(true); // 不解析实体

        // 解析 XML
        TXmlDocument doc(xmlContent, options);

        // 获取根元素
        auto root = doc.GetRootNode();
        std::cout << "Root element: " << root.GetName() << std::endl;

        // 遍历书籍
        auto books = root.GetChildNodes("book");
        std::cout << "Found " << books.Size() << " books:" << std::endl;

        for (size_t i = 0; i < books.Size(); ++i) {
            auto book = books[i];
            std::string id = book.GetAttribute("id");
            std::string title = book.GetChildNode("title").GetText();
            std::string author = book.GetChildNode("author").GetText();
            std::string price = book.GetChildNode("price").GetText();
            std::string currency = book.GetChildNode("price").GetAttribute("currency");

            std::cout << "  Book " << id << ": " << title
                      << " by " << author
                      << " (" << price << " " << currency << ")" << std::endl;

            // 获取分类
            auto categories = book.GetChildNode("categories").GetChildNodes("category");
            std::cout << "    Categories: ";
            for (size_t j = 0; j < categories.Size(); ++j) {
                std::cout << categories[j].GetText();
                if (j + 1 < categories.Size()) {
                    std::cout << ", ";
                }
            }
            std::cout << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "XML parsing error: " << e.what() << std::endl;
    }
}
```

### XPath 查询

```cpp
#include <library/cpp/xml/document/xml-document.h>

void XPathExample() {
    NYXml::TInitializeGuard xmlGuard;

    TString xmlContent = R"(<?xml version="1.0" encoding="UTF-8"?>
<library>
    <section name="Computer Science">
        <book id="1" year="2020" available="true">
            <title>Modern C++ Design</title>
            <author>Andrei Alexandrescu</author>
            <publisher>Addison-Wesley</publisher>
            <details>
                <pages>352</pages>
                <isbn>978-0201704310</isbn>
                <rating>4.5</rating>
            </details>
        </book>
        <book id="2" year="2019" available="true">
            <title>The C++ Programming Language</title>
            <author>Bjarne Stroustrup</author>
            <publisher>Addison-Wesley</publisher>
            <details>
                <pages>1360</pages>
                <isbn>978-0201700732</isbn>
                <rating>4.8</rating>
            </details>
        </book>
        <book id="3" year="2018" available="false">
            <title>Effective Modern C++</title>
            <author>Scott Meyers</author>
            <publisher>O'Reilly</publisher>
            <details>
                <pages>320</pages>
                <isbn>978-1491903995</isbn>
                <rating>4.7</rating>
            </details>
        </book>
    </section>
    <section name="Software Engineering">
        <book id="4" year="2021" available="true">
            <title>Clean Architecture</title>
            <author>Robert C. Martin</author>
            <publisher>Prentice Hall</publisher>
            <details>
                <pages>432</pages>
                <isbn>978-0134494166</isbn>
                <rating>4.6</rating>
            </details>
        </book>
    </section>
</library>
)";

    try {
        TXmlDocument doc(xmlContent);

        // XPath 查询示例
        std::cout << "=== XPath Query Examples ===" << std::endl;

        // 1. 查找所有书籍
        auto allBooks = doc.Query("//book");
        std::cout << "1. All books (" << allBooks.Size() << "):" << std::endl;
        for (size_t i = 0; i < allBooks.Size(); ++i) {
            auto book = allBooks[i];
            auto title = book.GetChildNode("title").GetText();
            std::cout << "   - " << title << std::endl;
        }

        // 2. 查找特定作者的书籍
        auto stroustrupBooks = doc.Query("//book[author='Bjarne Stroustrup']");
        std::cout << "\n2. Books by Bjarne Stroustrup:" << std::endl;
        for (size_t i = 0; i < stroustrupBooks.Size(); ++i) {
            auto book = stroustrupBooks[i];
            auto title = book.GetChildNode("title").GetText();
            std::cout << "   - " << title << std::endl;
        }

        // 3. 查找2020年后出版的书籍
        auto recentBooks = doc.Query("//book[@year > 2020]");
        std::cout << "\n3. Books published after 2020:" << std::endl;
        for (size_t i = 0; i < recentBooks.Size(); ++i) {
            auto book = recentBooks[i];
            auto title = book.GetChildNode("title").GetText();
            int year = std::stoi(book.GetAttribute("year"));
            std::cout << "   - " << title << " (" << year << ")" << std::endl;
        }

        // 4. 查找评分高于4.5的可用书籍
        auto highlyRatedAvailableBooks = doc.Query("//book[@available='true' and details/rating > 4.5]");
        std::cout << "\n4. Highly rated available books:" << std::endl;
        for (size_t i = 0; i < highlyRatedAvailableBooks.Size(); ++i) {
            auto book = highlyRatedAvailableBooks[i];
            auto title = book.GetChildNode("title").GetText();
            auto rating = book.GetChildNode("details").GetChildNode("rating").GetText();
            std::cout << "   - " << title << " (rating: " << rating << ")" << std::endl;
        }

        // 5. 查找页面数少于400页的书籍
        auto shortBooks = doc.Query("//book[details/pages < 400]");
        std::cout << "\n5. Books with less than 400 pages:" << std::endl;
        for (size_t i = 0; i < shortBooks.Size(); ++i) {
            auto book = shortBooks[i];
            auto title = book.GetChildNode("title").GetText();
            auto pages = book.GetChildNode("details").GetChildNode("pages").GetText();
            std::cout << "   - " << title << " (" << pages << " pages)" << std::endl;
        }

        // 6. 计算函数使用
        auto avgRating = doc.Query("sum(//book/details/rating) div count(//book/details/rating)");
        std::cout << "\n6. Average book rating: " << avgRating.GetText() << std::endl;

        // 7. 条件计数
        auto availableCount = doc.Query("count(//book[@available='true'])");
        std::cout << "7. Available books count: " << availableCount.GetText() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "XPath query error: " << e.what() << std::endl;
    }
}
```

### XML 文档生成

```cpp
void XMLGenerationExample() {
    NYXml::TInitializeGuard xmlGuard;

    try {
        // 创建新文档
        TXmlDocument doc;

        // 创建根元素
        auto root = doc.CreateRootNode("employees");

        // 添加第一个员工
        auto employee1 = root.CreateChildNode("employee");
        employee1.SetAttribute("id", "1001");
        employee1.SetAttribute("status", "active");

        auto name1 = employee1.CreateChildNode("name");
        name1.CreateChildNode("first").SetText("John");
        name1.CreateChildNode("last").SetText("Doe");

        auto position1 = employee1.CreateChildNode("position");
        position1.SetText("Senior Software Engineer");

        auto department1 = employee1.CreateChildNode("department");
        department1.SetText("Engineering");

        auto contact1 = employee1.CreateChildNode("contact");
        contact1.CreateChildNode("email").SetText("john.doe@company.com");
        contact1.CreateChildNode("phone").SetText("+1-555-0101");

        auto skills1 = employee1.CreateChildNode("skills");
        skills1.CreateChildNode("skill").SetText("C++");
        skills1.CreateChildNode("skill").SetText("Python");
        skills1.CreateChildNode("skill").SetText("System Design");

        // 添加第二个员工
        auto employee2 = root.CreateChildNode("employee");
        employee2.SetAttribute("id", "1002");
        employee2.SetAttribute("status", "active");

        auto name2 = employee2.CreateChildNode("name");
        name2.CreateChildNode("first").SetText("Jane");
        name2.CreateChildNode("last").SetText("Smith");

        auto position2 = employee2.CreateChildNode("position");
        position2.SetText("Product Manager");

        auto department2 = employee2.CreateChildNode("department");
        department2.SetText("Product");

        auto contact2 = employee2.CreateChildNode("contact");
        contact2.CreateChildNode("email").SetText("jane.smith@company.com");
        contact2.CreateChildNode("phone").SetText("+1-555-0102");

        auto skills2 = employee2.CreateChildNode("skills");
        skills2.CreateChildNode("skill").SetText("Product Strategy");
        skills2.CreateChildNode("skill").SetText("User Research");
        skills2.CreateChildNode("skill").SetText("Agile");

        // 生成 XML 字符串
        TString xmlOutput = doc.ToString(true); // true = 格式化输出
        std::cout << "Generated XML:\n" << xmlOutput << std::endl;

        // 保存到文件
        TUnbufferedFileOutput fileOutput("employees.xml");
        fileOutput << xmlOutput;
        std::cout << "XML saved to employees.xml" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "XML generation error: " << e.what() << std::endl;
    }
}
```

### 流式处理大文件

```cpp
#include <library/cpp/xml/document/xml-textreader.h>

void StreamingXMLProcessing() {
    NYXml::TInitializeGuard xmlGuard;

    // 创建大型 XML 文件用于演示
    {
        TUnbufferedFileOutput output("large_data.xml");
        output << R"(<?xml version="1.0" encoding="UTF-8"?>
<products>
)";

        // 生成大量产品数据
        for (int i = 1; i <= 100000; ++i) {
            output << "    <product id=\"" << i << "\" category=\""
                   << ((i % 3 == 0) ? "electronics" : (i % 3 == 1) ? "books" : "clothing")
                   << "\" in_stock=\"" << ((i % 4 == 0) ? "false" : "true") << "\">\n";
            output << "        <name>Product " << i << "</name>\n";
            output << "        <price>" << (10.0 + (i % 100)) << "</price>\n";
            output << "        <description>This is product number " << i << "</description>\n";
            output << "    </product>\n";
        }

        output << "</products>\n";
    }

    // 使用 XmlTextReader 进行流式处理
    try {
        TUnbufferedFileInput input("large_data.xml");
        TXmlTextReader reader(&input);

        std::atomic<int> productCount{0};
        std::atomic<double> totalValue{0.0};
        std::map<std::string, int> categoryCount;
        std::atomic<int> outOfStockCount{0};

        // 流式解析
        while (reader.Read()) {
            const auto& nodeType = reader.GetNodeType();

            if (nodeType == TXmlTextReader::NodeType::StartElement) {
                std::string nodeName = reader.GetLocalName();

                if (nodeName == "product") {
                    productCount++;

                    // 读取属性
                    std::string id = reader.GetAttribute("id");
                    std::string category = reader.GetAttribute("category");
                    std::string inStock = reader.GetAttribute("in_stock");

                    categoryCount[category]++;

                    if (inStock == "false") {
                        outOfStockCount++;
                    }

                    // 读取产品详情
                    std::string name, price, description;
                    bool inProduct = true;

                    while (inProduct && reader.Read()) {
                        if (reader.GetNodeType() == TXmlTextReader::NodeType::StartElement) {
                            std::string childNodeName = reader.GetLocalName();

                            if (childNodeName == "name") {
                                if (reader.Read() && reader.GetNodeType() == TXmlTextReader::NodeType::Text) {
                                    name = reader.GetValue();
                                }
                            } else if (childNodeName == "price") {
                                if (reader.Read() && reader.GetNodeType() == TXmlTextReader::NodeType::Text) {
                                    price = reader.GetValue();
                                    totalValue += std::stod(price);
                                }
                            } else if (childNodeName == "description") {
                                if (reader.Read() && reader.GetNodeType() == TXmlTextReader::NodeType::Text) {
                                    description = reader.GetValue();
                                }
                            }
                        } else if (reader.GetNodeType() == TXmlTextReader::NodeType::EndElement &&
                                 reader.GetLocalName() == "product") {
                            inProduct = false;
                        }
                    }

                    // 处理每1000个产品报告一次进度
                    if (productCount % 1000 == 0) {
                        std::cout << "Processed " << productCount.load() << " products..." << std::endl;
                    }
                }
            }
        }

        // 输出统计结果
        std::cout << "\n=== Processing Results ===" << std::endl;
        std::cout << "Total products: " << productCount.load() << std::endl;
        std::cout << "Total value: $" << std::fixed << std::setprecision(2) << totalValue.load() << std::endl;
        std::cout << "Out of stock: " << outOfStockCount.load() << std::endl;

        std::cout << "\nProducts by category:" << std::endl;
        for (const auto& [category, count] : categoryCount) {
            std::cout << "  " << category << ": " << count << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "Streaming XML processing error: " << e.what() << std::endl;
    }
}
```

### 命名空间处理

```cpp
void NamespaceExample() {
    NYXml::TInitializeGuard xmlGuard;

    TString xmlWithNamespaces = R"(<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:book="http://example.com/books"
      xmlns:auth="http://example.com/authors"
      xmlns="http://example.com/library">

    <book:catalog>
        <book:item book:id="1">
            <title>Advanced C++</title>
            <auth:author auth:country="USA">
                <auth:name>Andrew Koenig</auth:name>
                <auth:affiliation>AT&T</auth:affiliation>
            </auth:author>
            <price currency="USD">59.99</price>
        </book:item>

        <book:item book:id="2">
            <title>Modern C++ Design</title>
            <auth:author auth:country="Canada">
                <auth:name>Andrei Alexandrescu</auth:name>
                <auth:affiliation>Facebook</auth:affiliation>
            </auth:author>
            <price currency="USD">49.99</price>
        </book:item>
    </book:catalog>
</root>
)";

    try {
        NYXml::TXmlOptions options;
        options.SetNamespaceProcessing(true);

        TXmlDocument doc(xmlWithNamespaces, options);

        // 注册命名空间前缀
        doc.RegisterNamespace("book", "http://example.com/books");
        doc.RegisterNamespace("auth", "http://example.com/authors");
        doc.RegisterNamespace("lib", "http://example.com/library");

        std::cout << "=== Namespace Processing ===" << std::endl;

        // 使用命名空间前缀进行 XPath 查询
        auto books = doc.Query("//book:item");
        std::cout << "Found " << books.Size() << " books:" << std::endl;

        for (size_t i = 0; i < books.Size(); ++i) {
            auto book = books[i];
            std::string id = book.GetAttribute("book:id");
            std::string title = book.GetChildNode("title").GetText();
            std::string price = book.GetChildNode("price").GetText();

            // 获取作者信息（使用命名空间）
            auto author = book.GetChildNode("auth:author");
            std::string authorName = author.GetChildNode("auth:name").GetText();
            std::string authorCountry = author.GetAttribute("auth:country");

            std::cout << "  Book " << id << ": " << title << std::endl;
            std::cout << "    Author: " << authorName << " (" << authorCountry << ")" << std::endl;
            std::cout << "    Price: " << price << std::endl;
        }

        // 查询特定国家的作者
        auto usAuthors = doc.Query("//auth:author[@auth:country='USA']");
        std::cout << "\nAuthors from USA:" << std::endl;
        for (size_t i = 0; i < usAuthors.Size(); ++i) {
            auto author = usAuthors[i];
            auto name = author.GetChildNode("auth:name").GetText();
            auto affiliation = author.GetChildNode("auth:affiliation").GetText();
            std::cout << "  - " << name << " (" << affiliation << ")" << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "Namespace processing error: " << e.what() << std::endl;
    }
}
```

### XML 验证

```cpp
void ValidationExample() {
    NYXml::TInitializeGuard xmlGuard;

    // XML Schema
    TString xmlSchema = R"(<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:element name="employees">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="employee" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="name" type="xs:string"/>
                            <xs:element name="email" type="xs:string"/>
                            <xs:element name="age" type="xs:positiveInteger"/>
                            <xs:element name="department" type="xs:string"/>
                        </xs:sequence>
                        <xs:attribute name="id" type="xs:positiveInteger" use="required"/>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>

</xs:schema>
)";

    // 有效的 XML
    TString validXml = R"(<?xml version="1.0" encoding="UTF-8"?>
<employees>
    <employee id="1">
        <name>John Doe</name>
        <email>john.doe@company.com</email>
        <age>30</age>
        <department>Engineering</department>
    </employee>
    <employee id="2">
        <name>Jane Smith</name>
        <email>jane.smith@company.com</email>
        <age>28</age>
        <department>Product</department>
    </employee>
</employees>
)";

    // 无效的 XML
    TString invalidXml = R"(<?xml version="1.0" encoding="UTF-8"?>
<employees>
    <employee>
        <!-- 缺少必需的 id 属性 -->
        <name>Bob Wilson</name>
        <email>bob.wilson@company.com</email>
        <age>-5</age>  <!-- 无效的年龄 -->
        <!-- 缺少 department 元素 -->
    </employee>
</employees>
)";

    try {
        // 创建验证器
        TXmlValidator validator;
        validator.LoadSchema(xmlSchema);

        std::cout << "=== XML Validation ===" << std::endl;

        // 验证有效的 XML
        std::cout << "\nValidating valid XML..." << std::endl;
        auto validResult = validator.Validate(validXml);
        if (validResult.IsValid()) {
            std::cout << "✓ XML is valid" << std::endl;
        } else {
            std::cout << "✗ XML validation failed:" << std::endl;
            for (const auto& error : validResult.GetErrors()) {
                std::cout << "  - " << error << std::endl;
            }
        }

        // 验证无效的 XML
        std::cout << "\nValidating invalid XML..." << std::endl;
        auto invalidResult = validator.Validate(invalidXml);
        if (invalidResult.IsValid()) {
            std::cout << "✓ XML is valid" << std::endl;
        } else {
            std::cout << "✗ XML validation failed:" << std::endl;
            for (const auto& error : invalidResult.GetErrors()) {
                std::cout << "  - " << error << std::endl;
            }
        }

    } catch (const std::exception& e) {
        std::cerr << "XML validation error: " << e.what() << std::endl;
    }
}
```

## 🔧 高级特性

### 安全 XML 解析

```cpp
void SecureXMLProcessing() {
    NYXml::TInitializeGuard xmlGuard;

    // 配置安全的解析选项
    NYXml::TXmlOptions secureOptions;
    secureOptions.SetNoEntities(true);           // 禁用实体扩展，防止 XXE
    secureOptions.SetNoNetwork(true);            // 禁用网络访问
    secureOptions.SetLoadExternalDTD(false);     // 不加载外部 DTD
    secureOptions.SetParseDTD(false);            // 不解析 DTD
    secureOptions.SetXInclude(false);            // 禁用 XInclude

    // 潜在恶意 XML（包含 XXE 攻击）
    TString maliciousXml = R"(<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
    <data>&xxe;</data>
</root>
)";

    try {
        std::cout << "Processing potentially malicious XML..." << std::endl;

        // 使用安全选项解析
        TXmlDocument doc(maliciousXml, secureOptions);

        std::cout << "XML parsed safely (XXE blocked)" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "XML parsing failed: " << e.what() << std::endl;
    }
}
```

## 🧪 测试和验证

### 性能测试

```cpp
#include <library/cpp/testing/gtest/gtest.h>
#include <chrono>

class XMLPerformanceTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 生成大型测试 XML
        GenerateTestXML(10000); // 10K elements
    }

    void GenerateTestXML(size_t count) {
        TUnbufferedFileOutput output("performance_test.xml");
        output << R"(<?xml version="1.0" encoding="UTF-8"?>
<data>
)";

        for (size_t i = 0; i < count; ++i) {
            output << "    <item id=\"" << i << "\" category=\"cat" << (i % 10) << "\">";
            output << "value" << i << "</item>\n";
        }

        output << "</data>\n";
        TestXMLSize_ = count;
    }

    size_t TestXMLSize_;
};

TEST_F(XMLPerformanceTest, DOMParsingPerformance) {
    NYXml::TInitializeGuard xmlGuard;

    auto start = std::chrono::high_resolution_clock::now();

    TUnbufferedFileInput input("performance_test.xml");
    TString content;
    TStringOutput stringOutput(content);
    TransferData(&input, &stringOutput);

    TXmlDocument doc(content);

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "DOM parsing of " << TestXMLSize_ << " elements took "
              << duration.count() << " ms" << std::endl;

    // 验证解析结果
    auto items = doc.Query("//item");
    EXPECT_EQ(items.Size(), TestXMLSize_);
}

TEST_F(XMLPerformanceTest, XPathPerformance) {
    NYXml::TInitializeGuard xmlGuard;

    TUnbufferedFileInput input("performance_test.xml");
    TString content;
    TStringOutput stringOutput(content);
    TransferData(&input, &stringOutput);

    TXmlDocument doc(content);

    auto start = std::chrono::high_resolution_clock::now();

    // 执行多个 XPath 查询
    for (int i = 0; i < 100; ++i) {
        auto result = doc.Query("//item[@id < 1000]");
        EXPECT_FALSE(result.Empty());
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "100 XPath queries on " << TestXMLSize_
              << " elements took " << duration.count() << " ms" << std::endl;
}
```

## 📈 最佳实践

### 性能优化建议

1. **大文件处理**: 使用 `TXmlTextReader` 进行流式处理
2. **内存管理**: 及时释放不再需要的文档对象
3. **查询优化**: 使用具体的 XPath 表达式
4. **缓存策略**: 缓存频繁查询的结果
5. **解析选项**: 根据需求配置合适的解析选项

### 安全建议

1. **XXE 防护**: 禁用实体扩展和外部 DTD
2. **输入验证**: 验证所有 XML 输入
3. **资源限制**: 设置合理的解析限制
4. **错误处理**: 妥善处理解析错误

### 错误处理

```cpp
void RobustXMLProcessing() {
    NYXml::TInitializeGuard xmlGuard;

    try {
        TXmlDocument doc("input.xml", NYXml::TXmlOptions::GetDefault());

        // 处理 XML...

    } catch (const TXmlParseException& e) {
        std::cerr << "XML Parse Error: " << e.what() << std::endl;
        std::cerr << "Line: " << e.GetLineNumber()
                  << ", Column: " << e.GetColumnNumber() << std::endl;

    } catch (const TXmlValidationException& e) {
        std::cerr << "XML Validation Error: " << e.what() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "XML Processing Error: " << e.what() << std::endl;
    }
}
```

## 🔗 相关模块

- **YAML**: 配置文件处理
- **JSON**: JSON 数据处理
- **Streams**: 文件和流处理
- **StringUtils**: 字符串处理工具
- **FileSystem**: 文件系统操作

XML 库为 YTsaurus 提供了完整的 XML 处理能力，从简单的小型配置文件到大型数据流的处理，支持 XPath 查询、命名空间、验证等高级特性，是处理结构化数据的重要工具。