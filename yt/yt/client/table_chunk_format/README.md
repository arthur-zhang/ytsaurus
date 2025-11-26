# YTsaurus Table Chunk Format 模块

## 概述

Table Chunk Format 模块定义了 YTsaurus 表数据的分片存储格式，包括数据编码、压缩和索引结构。

## 核心功能

- **数据编码**: 表数据的高效编码格式
- **压缩支持**: 多种压缩算法支持
- **索引结构**: 快速数据检索索引

## 依赖项

- `yt/yt/core/misc/public.h`

## 相关模块

- **Table Client**: 表数据操作
- **Chunk Client**: 分片存储

## 贡献指南

确保数据格式的高效性和兼容性。