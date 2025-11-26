# CRC64

## 概述

CRC64 模块实现了 YTsaurus 系统中使用的特定 CRC64 校验和算法。该模块提供了一个与 YTsaurus C++ 代码兼容的 CRC64 实现，用于数据完整性验证和错误检测。

## 功能特性

- **标准兼容**：与 YTsaurus C++ 实现完全兼容
- **高效计算**：使用预计算查找表优化性能
- **流式处理**：支持分块计算校验和
- **标准接口**：实现 Go 标准库的 `hash.Hash64` 接口

## 算法参数

CRC64 算法使用以下参数（与 YTsaurus C++ 代码一致）：

- **多项式**：自定义多项式
- **初始值**：0x0000000000000000
- **输入反转**：无
- **输出反转**：字节反转
- **异或输出**：0x0000000000000000

## 核心接口

### Hash 接口实现

```go
type digest struct {
    crc uint64  // 当前 CRC64 值
}

// 实现 hash.Hash64 接口
func (d *digest) Write(p []byte) (n int, err error)
func (d *digest) Sum(b []byte) []byte
func (d *digest) Sum64() uint64
func (d *digest) Reset()
func (d *digest) Size() int
func (d *digest) BlockSize() int
```

## 使用方法

### 基本用法

```go
package main

import (
    "fmt"
    "io"

    "go.ytsaurus.tech/yt/go/crc64"
)

func main() {
    // 计算字节数组的 CRC64
    data := []byte("Hello, YTsaurus!")
    checksum := crc64.Checksum(data)
    fmt.Printf("CRC64: %016x\n", checksum)

    // 使用 Hash 接口
    h := crc64.New()
    h.Write(data)
    fmt.Printf("CRC64 (Hash): %016x\n", h.Sum64())
}
```

### 流式计算

```go
func streamChecksum() error {
    // 创建新的 CRC64 计算器
    h := crc64.New()

    // 从文件流式读取并计算校验和
    file, err := os.Open("large_file.dat")
    if err != nil {
        return err
    }
    defer file.Close()

    // 创建缓冲区分块读取
    buf := make([]byte, 4096)
    for {
        n, err := file.Read(buf)
        if err != nil && err != io.EOF {
            return err
        }
        if n == 0 {
            break
        }

        // 更新校验和
        if _, err := h.Write(buf[:n]); err != nil {
            return err
        }
    }

    checksum := h.Sum64()
    fmt.Printf("文件校验和: %016x\n", checksum)
    return nil
}
```

### 组合数据校验

```go
func combineDataChecksum() {
    h := crc64.New()

    // 写入多个数据块
    h.Write([]byte("Block 1: "))
    h.Write([]byte("Some data"))
    h.Write([]byte("\n"))
    h.Write([]byte("Block 2: "))
    h.Write([]byte("More data"))

    // 获取完整校验和
    checksum := h.Sum64()
    fmt.Printf("组合数据校验和: %016x\n", checksum)

    // 获取字节形式的校验和
    checksumBytes := h.Sum(nil)
    fmt.Printf("校验和字节: %x\n", checksumBytes)
}
```

### 重用计算器

```go
func reuseCalculator() {
    h := crc64.New()

    // 第一次计算
    h.Write([]byte("Data set 1"))
    checksum1 := h.Sum64()
    fmt.Printf("数据集1校验和: %016x\n", checksum1)

    // 重置计算器
    h.Reset()

    // 第二次计算
    h.Write([]byte("Data set 2"))
    checksum2 := h.Sum64()
    fmt.Printf("数据集2校验和: %016x\n", checksum2)
}
```

## 性能优化

### 预计算表

模块使用 256 项的预计算查找表来加速 CRC64 计算：

```go
var table = crc64.Table{
    // 256 个预计算的 CRC64 值
}
```

### 批量处理建议

对于大数据处理，建议使用适当的块大小：

```go
const optimalBlockSize = 64 * 1024 // 64KB

func optimizedChecksum(data []byte) uint64 {
    h := crc64.New()

    for i := 0; i < len(data); i += optimalBlockSize {
        end := i + optimalBlockSize
        if end > len(data) {
            end = len(data)
        }
        h.Write(data[i:end])
    }

    return h.Sum64()
}
```

## 实际应用场景

### 1. 数据完整性验证

```go
func verifyDataIntegrity(original, received []byte) bool {
    originalChecksum := crc64.Checksum(original)
    receivedChecksum := crc64.Checksum(received)
    return originalChecksum == receivedChecksum
}
```

### 2. 文件校验

```go
func computeFileChecksum(filename string) (uint64, error) {
    h := crc64.New()

    file, err := os.Open(filename)
    if err != nil {
        return 0, err
    }
    defer file.Close()

    if _, err := io.Copy(h, file); err != nil {
        return 0, err
    }

    return h.Sum64(), nil
}
```

### 3. 网络传输验证

```go
func sendDataWithChecksum(conn net.Conn, data []byte) error {
    // 计算校验和
    checksum := crc64.Checksum(data)

    // 发送数据长度
    if err := binary.Write(conn, binary.LittleEndian, uint64(len(data))); err != nil {
        return err
    }

    // 发送数据
    if _, err := conn.Write(data); err != nil {
        return err
    }

    // 发送校验和
    return binary.Write(conn, binary.LittleEndian, checksum)
}
```

## 测试

模块包含基本的单元测试：

```go
func TestCRC64(t *testing.T) {
    // 测试已知值的校验和
    data := []byte("test")
    expected := uint64(0x...)
    actual := crc64.Checksum(data)
    assert.Equal(t, expected, actual)
}
```

## 注意事项

1. **字节序**：输出使用小端字节序（Little Endian）
2. **线程安全**：单个 `digest` 实例不是线程安全的
3. **内存使用**：查找表占用 2KB 内存
4. **性能考虑**：对于小数据块，初始化开销可能较大
5. **兼容性**：确保与 YTsaurus C++ 版本使用相同的参数

## 技术细节

### 算法实现

CRC64 计算的核心实现：

```go
func (d *digest) update(p []byte) {
    d.crc = ^crc64.Update(^d.crc, &table, p)
}

func (d *digest) Sum64() uint64 {
    return bits.ReverseBytes64(d.crc)
}
```

### 关键特性

1. **输入反转**：使用按位取反 (`^`) 实现输入反转
2. **输出反转**：使用 `bits.ReverseBytes64` 实现字节反转
3. **增量更新**：支持分块更新 CRC64 值
4. **零初始化**：初始 CRC64 值为 0

## 依赖项

- Go 标准库 `hash/crc64`：基础 CRC64 实现
- Go 标准库 `encoding/binary`：二进制编码
- Go 标准库 `math/bits`：位操作函数
- Go 标准库 `hash`：Hash 接口定义