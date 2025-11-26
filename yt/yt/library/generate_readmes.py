#!/usr/bin/env python3
"""
批量生成 README.md 文件的脚本
为所有没有中文 README 的子文件夹生成文档
"""

import os
import subprocess
import sys
from pathlib import Path

def get_all_subdirs():
    """获取所有非隐藏子文件夹"""
    subdirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith('.'):
            subdirs.append(item)
    return sorted(subdirs)

def has_chinese_readme(dirname):
    """检查是否已有中文 README"""
    readme_files = ['README.md', 'README_zh.md', 'readme.md', 'readme_zh.md']
    for rf in readme_files:
        filepath = os.path.join(dirname, rf)
        if os.path.exists(filepath):
            # 读取文件前几行检查是否是中文
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_lines = ''.join(f.readlines()[:5])
                    # 检查是否包含中文字符
                    if any('\u4e00' <= char <= '\u9fff' for char in first_lines):
                        return True
            except:
                pass
    return False

def analyze_and_generate_readme(dirname):
    """分析文件夹并生成 README"""
    print(f"\n{'='*60}")
    print(f"正在处理文件夹: {dirname}")
    print(f"{'='*60}")

    # 使用 Claude Code 分析并生成 README
    cmd = f'''claude-code --message "
请详细分析 ./{dirname} 文件夹的内容：
1. 列出所有文件和子文件夹
2. 读取主要的源代码文件（.cpp .h .hpp .proto .py 等）
3. 分析代码功能和用途
4. 理解这个模块的实现原理
5. 找出依赖关系
6. 为这个文件夹生成一个专业的中文 README.md 文件

要求：
- README 必须使用中文编写
- 包含项目描述、主要功能、文件说明、使用方法、依赖项、实现原理
- 如果是测试文件夹，说明测试的目的和覆盖范围
- 代码示例要准确实用
- 技术细节要准确

请直接生成完整的 README.md 文件内容，我会将其写入到 ./{dirname}/README.md
"
'''

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ 成功分析 {dirname}")
            # 保存分析结果
            with open(f'./{dirname}/README.md', 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"✓ 已生成 {dirname}/README.md")
            return True
        else:
            print(f"✗ 分析 {dirname} 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 处理 {dirname} 时出错: {str(e)}")
        return False

def main():
    print("开始批量生成 README.md 文件...")
    print("当前工作目录:", os.getcwd())

    # 获取所有子文件夹
    subdirs = get_all_subdirs()
    print(f"\n找到 {len(subdirs)} 个子文件夹")

    # 统计
    total = len(subdirs)
    processed = 0
    skipped = 0
    success = 0

    # 处理每个文件夹
    for dirname in subdirs:
        processed += 1

        # 检查是否已有中文 README
        if has_chinese_readme(dirname):
            print(f"\n[{processed}/{total}] {dirname}: 已有中文 README，跳过")
            skipped += 1
            continue

        print(f"\n[{processed}/{total}] {dirname}: 需要生成 README")

        # 分析并生成 README
        if analyze_and_generate_readme(dirname):
            success += 1

    # 输出统计信息
    print(f"\n{'='*60}")
    print(f"批量处理完成！")
    print(f"总文件夹数: {total}")
    print(f"已处理: {processed}")
    print(f"跳过已有 README: {skipped}")
    print(f"成功生成: {success}")
    print(f"失败: {processed - skipped - success}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()