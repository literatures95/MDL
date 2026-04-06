#!/usr/bin/env python3
"""
MDL 构建脚本 - 使用 Pandoc 和 ConTeXt 生成专业 PDF

基于 Dave Jarvis 的排版文章: https://dave.autonoma.ca/blog/2019/05/22/typesetting-markdown-part-1/

用法:
    python build.py document.md                    # 使用默认模板
    python build.py document.md --template tech    # 使用技术文档模板
    python build.py document.md --watch            # 监听文件变化并重新构建
"""

import argparse
import os
import sys
import time
import subprocess
import shutil
from pathlib import Path
from typing import Optional


class PDFBuilder:
    """PDF 构建器"""

    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.templates = {
            "default": self.template_dir / "default.ctx",
            "technical": self.template_dir / "technical.ctx",
            "book": self.template_dir / "book.ctx",  # 未来添加
        }

    def check_dependencies(self):
        """检查必要的依赖"""
        missing = []

        if not shutil.which("pandoc"):
            missing.append("pandoc (https://pandoc.org/installing.html)")

        if not shutil.which("context"):
            missing.append("context (https://wiki.contextgarden.net/Installation)")

        if missing:
            print("缺少必要的依赖:")
            for dep in missing:
                print(f"  - {dep}")
            sys.exit(1)

    def build_pdf(self, input_file: str, output_file: Optional[str] = None,
                  template: str = "default", paper_size: str = "a4",
                  font_size: int = 11, margins: str = "2.5cm") -> str:
        """构建 PDF"""

        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        # 确定输出文件
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = input_path.with_suffix('.pdf')

        # 检查模板
        if template not in self.templates:
            available = ", ".join(self.templates.keys())
            raise ValueError(f"未知模板 '{template}'，可用模板: {available}")

        template_path = self.templates[template]
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

        print(f"构建 PDF: {input_path} -> {output_path}")
        print(f"使用模板: {template} ({template_path})")

        # 构建 Pandoc 命令
        cmd = [
            "pandoc",
            str(input_path),
            "-f", "markdown+smart+yaml_metadata_block+footnotes+inline_notes+table_captions",
            "-t", "context",
            "-o", str(output_path),
            "--pdf-engine=context",
            "--template", str(template_path),
            f"--variable=fontsize={font_size}pt",
            f"--variable=papersize={paper_size}",
            f"--variable=margin={margins}",
            "--variable=colorlinks=true",
            "--variable=linkcolor=blue",
            "--variable=urlcolor=blue",
            "--variable=toccolor=black",
            "--toc",  # 生成目录
            "--toc-depth=3",
            "--number-sections",  # 章节编号
        ]

        print(f"执行: {' '.join(cmd)}")

        # 运行命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"构建失败:")
            print(f"错误输出: {result.stderr}")
            raise RuntimeError(f"Pandoc 错误: {result.stderr}")

        print(f"PDF 生成成功: {output_path}")
        return str(output_path)

    def watch_and_build(self, input_file: str, template: str = "default", **kwargs):
        """监听文件变化并重新构建"""
        print(f"监听文件: {input_file}")
        print("按 Ctrl+C 停止监听")

        last_mtime = os.path.getmtime(input_file)

        try:
            while True:
                time.sleep(1)
                current_mtime = os.path.getmtime(input_file)
                if current_mtime > last_mtime:
                    print(f"\n文件已修改，重新构建...")
                    try:
                        self.build_pdf(input_file, template=template, **kwargs)
                        print("构建完成")
                    except Exception as e:
                        print(f"构建失败: {e}")
                    last_mtime = current_mtime
        except KeyboardInterrupt:
            print("\n停止监听")


def main():
    parser = argparse.ArgumentParser(
        description="MDL PDF 构建器 - 使用 Pandoc 和 ConTeXt 生成专业文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build.py document.md                          # 使用默认模板
  python build.py document.md -t technical             # 使用技术文档模板
  python build.py document.md -o output.pdf            # 指定输出文件
  python build.py document.md --watch                  # 监听文件变化
  python build.py document.md --paper-size letter      # 纸张大小
  python build.py document.md --font-size 12           # 字体大小
        """
    )

    parser.add_argument("input", help="输入的 Markdown 文件")
    parser.add_argument("-o", "--output", help="输出 PDF 文件路径")
    parser.add_argument("-t", "--template", default="default",
                       choices=["default", "technical"],
                       help="使用的 ConTeXt 模板")
    parser.add_argument("--paper-size", default="a4",
                       choices=["a4", "letter", "a5", "b5"],
                       help="纸张大小")
    parser.add_argument("--font-size", type=int, default=11,
                       help="字体大小 (pt)")
    parser.add_argument("--margins", default="2.5cm",
                       help="页边距")
    parser.add_argument("--watch", action="store_true",
                       help="监听文件变化并自动重新构建")

    args = parser.parse_args()

    builder = PDFBuilder()

    # 检查依赖
    builder.check_dependencies()

    if args.watch:
        builder.watch_and_build(
            args.input,
            template=args.template,
            output_file=args.output,
            paper_size=args.paper_size,
            font_size=args.font_size,
            margins=args.margins
        )
    else:
        try:
            output = builder.build_pdf(
                args.input,
                output_file=args.output,
                template=args.template,
                paper_size=args.paper_size,
                font_size=args.font_size,
                margins=args.margins
            )
            print(f"\n构建完成: {output}")
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()