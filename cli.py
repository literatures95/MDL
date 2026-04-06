"""MDL 命令行工具 - 提供完整的命令行接口"""

import sys
import os
import argparse
import json
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="mdl",
        description="MDL - Markdown 操作语言，提供完美的 Markdown 解析、修改、转换和分析功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mdl convert document.pdf output.md        转换 PDF 为 Markdown
  mdl batch *.pdf output/ --format md       批量转换文件
  mdl analyze document.md                   分析文档
  mdl clean document.md -o cleaned.md       清理文档
  mdl extract document.md --schema full     提取结构化数据
  mdl repl                                  启动交互式环境
  mdl run script.mdl                        运行 MDL 脚本
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    convert_parser = subparsers.add_parser("convert", help="转换文档格式")
    convert_parser.add_argument("input", help="输入文件路径")
    convert_parser.add_argument("output", help="输出文件路径")
    convert_parser.add_argument("--format", "-f", default="md", choices=["md", "html", "json", "txt", "pdf"], help="输出格式")
    convert_parser.add_argument("--template", "-t", help="PDF 模板文件 (ConTeXt)")
    convert_parser.add_argument("--paper-size", default="a4", choices=["a4", "letter", "a5", "b5"], help="纸张大小")
    convert_parser.add_argument("--font-size", type=int, default=11, help="字体大小 (pt)")
    convert_parser.add_argument("--margins", default="2.5cm", help="页边距")
    convert_parser.add_argument("--clean", "-c", action="store_true", help="清理文档")
    convert_parser.add_argument("--llm", action="store_true", help="使用 LLM 增强")

    batch_parser = subparsers.add_parser("batch", help="批量处理文档")
    batch_parser.add_argument("input", nargs="+", help="输入文件模式 (支持通配符)")
    batch_parser.add_argument("output", help="输出目录")
    batch_parser.add_argument("--format", "-f", default="md", help="输出格式")
    batch_parser.add_argument("--clean", "-c", action="store_true", help="清理文档")
    batch_parser.add_argument("--workers", "-w", type=int, default=4, help="并行工作进程数")

    analyze_parser = subparsers.add_parser("analyze", help="分析文档")
    analyze_parser.add_argument("input", help="输入文件路径")
    analyze_parser.add_argument("--output", "-o", help="输出文件路径 (JSON)")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    clean_parser = subparsers.add_parser("clean", help="清理文档")
    clean_parser.add_argument("input", help="输入文件路径")
    clean_parser.add_argument("--output", "-o", help="输出文件路径")
    clean_parser.add_argument("--headers", action="store_true", help="移除页眉")
    clean_parser.add_argument("--footers", action="store_true", help="移除页脚")
    clean_parser.add_argument("--page-numbers", action="store_true", help="移除页码")

    extract_parser = subparsers.add_parser("extract", help="提取结构化数据")
    extract_parser.add_argument("input", help="输入文件路径")
    extract_parser.add_argument("--schema", "-s", default="basic", choices=["basic", "full", "custom"], help="提取模式")
    extract_parser.add_argument("--output", "-o", help="输出文件路径 (JSON)")
    extract_parser.add_argument("--llm", action="store_true", help="使用 LLM 增强")

    image_parser = subparsers.add_parser("images", help="提取图片")
    image_parser.add_argument("input", help="输入文件路径")
    image_parser.add_argument("--output", "-o", default="images", help="图片输出目录")
    image_parser.add_argument("--download", action="store_true", help="下载远程图片")

    repl_parser = subparsers.add_parser("repl", help="启动交互式环境")
    repl_parser.add_argument("--file", "-f", help="预加载的文件")

    run_parser = subparsers.add_parser("run", help="运行 MDL 脚本")
    run_parser.add_argument("script", help="脚本文件路径")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    eval_parser = subparsers.add_parser("eval", help="执行 MDL 代码")
    eval_parser.add_argument("code", help="MDL 代码")

    info_parser = subparsers.add_parser("info", help="显示系统信息")
    info_parser.add_argument("--formats", action="store_true", help="显示支持的格式")

    return parser


def cmd_convert(args):
    """转换命令"""
    from formats import convert_to_markdown
    from converter import md_to_html, md_to_text
    from cleaner import clean_document
    from md_parser import parse_markdown
    from md_generator import generate_markdown

    print(f"[MDL] 转换文件: {args.input}")

    try:
        md = convert_to_markdown(args.input)

        if args.clean:
            print("[MDL] 清理文档...")
            md = clean_document(md)

        if args.llm:
            try:
                from llm_enhancer import LLMEnhancer, LLMConfig
                print("[MDL] 使用 LLM 增强...")
                enhancer = LLMEnhancer(LLMConfig())
                result = enhancer.enhance_markdown(md)
                md = result.enhanced
                print(f"[MDL] 改进: {', '.join(result.improvements) or '无'}")
            except Exception as e:
                print(f"[MDL] LLM 增强失败: {e}")

        output_format = args.format.lower()
        if output_format in ("md", "markdown"):
            content = md
        elif output_format == "html":
            content = md_to_html(md)
        elif output_format == "txt":
            content = md_to_text(md)
        elif output_format == "json":
            doc = parse_markdown(md)
            content = json.dumps(doc.to_dict(), ensure_ascii=False, indent=2)
        elif output_format == "pdf":
            print("[MDL] 生成 PDF...")
            cmd_pdf_convert(md, args.output, getattr(args, 'template', None), getattr(args, 'paper_size', 'a4'), getattr(args, 'font_size', 11), getattr(args, 'margins', '2.5cm'))
            return  # PDF 生成函数会处理文件写入
        else:
            content = md

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[MDL] 输出已保存: {args.output}")
        print(f"[MDL] 文件大小: {len(content)} 字符")

    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_batch(args):
    """批量处理命令"""
    from batch import batch_convert

    print(f"[MDL] 批量处理: {args.input}")
    print(f"[MDL] 输出目录: {args.output}")

    try:
        report = batch_convert(
            args.input,
            args.output,
            args.format,
            clean=args.clean,
            max_workers=args.workers,
        )
        report.print_summary()
    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_analyze(args):
    """分析命令"""
    from formats import convert_to_markdown
    from analyzer import analyze
    from md_parser import parse_markdown

    print(f"[MDL] 分析文档: {args.input}")

    try:
        md = convert_to_markdown(args.input)
        doc = parse_markdown(md)
        stats = analyze(doc)

        if args.verbose:
            print("\n" + "=" * 50)
            print("文档分析报告")
            print("=" * 50)
            print(f"\n总元素数: {stats.total_elements}")
            print(f"总字数: {stats.word_count}")
            print(f"总行数: {stats.line_count}")
            print(f"\n元素统计:")
            for elem, count in stats.element_counts.items():
                print(f"  {elem}: {count}")
            if stats.heading_structure:
                print(f"\n标题结构:")
                for h in stats.heading_structure:
                    indent = "  " * (h["level"] - 1)
                    print(f"{indent}- {h['text']}")
            print()
        else:
            print(f"[MDL] 元素: {stats.total_elements}, 字数: {stats.word_count}, 行数: {stats.line_count}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(stats.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"[MDL] 报告已保存: {args.output}")

    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_clean(args):
    """清理命令"""
    from formats import convert_to_markdown
    from cleaner import clean_document, CleanerConfig

    print(f"[MDL] 清理文档: {args.input}")

    try:
        md = convert_to_markdown(args.input)

        config = CleanerConfig(
            remove_headers=args.headers,
            remove_footers=args.footers,
            remove_page_numbers=args.page_numbers,
        )
        cleaned = clean_document(md, config)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"[MDL] 输出已保存: {args.output}")
        else:
            print(cleaned)

    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_extract(args):
    """提取命令"""
    from formats import convert_to_markdown
    from extractor import extract_structured, DEFAULT_SCHEMAS

    print(f"[MDL] 提取数据: {args.input}")

    try:
        md = convert_to_markdown(args.input)

        if args.llm:
            try:
                from llm_enhancer import extract_structured_with_llm
                schema = DEFAULT_SCHEMAS.get(args.schema, DEFAULT_SCHEMAS["basic"])
                data = extract_structured_with_llm(md, schema)
            except Exception as e:
                print(f"[MDL] LLM 提取失败: {e}")
                data = extract_structured(md, args.schema)
        else:
            data = extract_structured(md, args.schema)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[MDL] 数据已保存: {args.output}")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_images(args):
    """图片提取命令"""
    from formats import convert_to_markdown
    from image_extractor import extract_images_from_markdown

    print(f"[MDL] 提取图片: {args.input}")

    try:
        md = convert_to_markdown(args.input)
        md, images = extract_images_from_markdown(
            md,
            args.output,
            download_remote=args.download,
        )

        print(f"[MDL] 提取了 {len(images)} 张图片")
        for img in images:
            print(f"  - {img['alt']}: {img['local']}")
        print(f"[MDL] 图片保存至: {args.output}")

    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_repl(args):
    """启动 REPL"""
    from repl import main_repl
    main_repl()


def cmd_run(args):
    """运行脚本"""
    from interpreter import Interpreter

    if not os.path.exists(args.script):
        print(f"[MDL] 错误: 文件不存在: {args.script}")
        sys.exit(1)

    print(f"[MDL] 运行脚本: {args.script}")

    try:
        interp = Interpreter()
        result = interp.run_file(args.script)
        if args.verbose and result:
            print(f"[MDL] 结果: {result}")
    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_eval(args):
    """执行代码"""
    from interpreter import Interpreter

    try:
        interp = Interpreter()
        result = interp.run_script(args.code)
        if result:
            print(result)
    except Exception as e:
        print(f"[MDL] 错误: {e}")
        sys.exit(1)


def cmd_info(args):
    """显示系统信息"""
    print("=" * 50)
    print("MDL - Markdown 操作语言")
    print("=" * 50)
    print(f"版本: 1.1.0")
    print(f"Python: {sys.version}")
    print(f"工作目录: {os.getcwd()}")

    if args.formats:
        from formats import get_supported_formats
        print("\n支持的格式:")
        formats = get_supported_formats()
        for ext, info in formats.items():
            status = "[OK]" if info.supported else "[--]"
            extra = f" (需要 {info.package})" if info.requires_extra else ""
            print(f"  {status} .{ext}: {info.name}{extra}")

    print()


def cmd_pdf_convert(md_content: str, output_path: str, template: str = None,
                   paper_size: str = "a4", font_size: int = 11, margins: str = "2.5cm"):
    """使用 Pandoc 和 ConTeXt 生成 PDF"""
    import tempfile
    import subprocess
    import shutil

    try:
        # 检查 Pandoc 是否可用
        if not shutil.which("pandoc"):
            raise Exception("需要安装 Pandoc: https://pandoc.org/installing.html")

        # 检查 ConTeXt 是否可用
        if not shutil.which("context"):
            raise Exception("需要安装 ConTeXt: https://wiki.contextgarden.net/Installation")

        # 创建临时 Markdown 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md_content)
            temp_md = f.name

        try:
            # 构建 Pandoc 命令
            cmd = [
                "pandoc",
                temp_md,
                "-f", "markdown",
                "-t", "context",
                "-o", output_path,
                "--pdf-engine=context",
                f"--variable=fontsize={font_size}pt",
                f"--variable=papersize={paper_size}",
                f"--variable=margin={margins}",
            ]

            # 如果指定了模板，添加模板选项
            if template and os.path.exists(template):
                cmd.extend(["--template", template])

            # 添加一些默认的 ConTeXt 选项用于更好的排版
            cmd.extend([
                "--variable=linkcolor=blue",
                "--variable=urlcolor=blue",
                "--variable=toccolor=black",
                "--variable=geometry=margin=2.5cm",
            ])

            print(f"[MDL] 执行命令: {' '.join(cmd)}")

            # 运行 Pandoc
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            if result.returncode != 0:
                print(f"[MDL] Pandoc 错误输出: {result.stderr}")
                raise Exception(f"Pandoc 转换失败: {result.stderr}")

            print(f"[MDL] PDF 已生成: {output_path}")

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_md)
            except:
                pass

    except Exception as e:
        print(f"[MDL] PDF 生成失败: {e}")
        sys.exit(1)


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "convert": cmd_convert,
        "batch": cmd_batch,
        "analyze": cmd_analyze,
        "clean": cmd_clean,
        "extract": cmd_extract,
        "images": cmd_images,
        "repl": cmd_repl,
        "run": cmd_run,
        "eval": cmd_eval,
        "info": cmd_info,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
