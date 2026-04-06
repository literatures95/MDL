"""MDL - Markdown 操作语言主入口"""

import sys
import os
from interpreter import Interpreter


def print_usage():
    """打印使用说明"""
    usage = """
╔═══════════════════════════════════════════════════╗
║           MDL - Markdown 操作语言 v1.0              ║
║     Markdown Operation & Analysis Language          ║
╠═══════════════════════════════════════════════════╣
║                                                     ║
║  用法:                                               ║
║    python mdl.py <脚本文件.mdl>    运行 MDL 脚本      ║
║    python mdl.py -e "代码"         执行单行代码       ║
║    python mdl.py                  启动交互式 REPL   ║
║    python mdl.py --repl           启动交互式 REPL   ║
║                                                     ║
║  示例:                                               ║
║    python mdl.py example.mdl                       ║
║    python mdl.py -e 'load "test.md"; print doc.h1'  ║
║                                                     ║
╚═══════════════════════════════════════════════════╝
"""
    print(usage)


def run_file(filepath: str):
    """运行 MDL 脚本文件"""
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在: {filepath}")
        sys.exit(1)
    interpreter = Interpreter()
    try:
        result = interpreter.run_file(filepath)
        return result
    except Exception as e:
        print(f"执行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_eval(code: str):
    """执行单行/多行代码"""
    interpreter = Interpreter()
    try:
        result = interpreter.run_script(code)
        return result
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


def main():
    """主入口函数"""
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print_usage()
        if "--help" in args or "-h" in args:
            sys.exit(0)
        from repl import main_repl
        main_repl()
        return
    if args[0] == "--repl":
        from repl import main_repl
        main_repl()
        return
    if args[0] == "-e" and len(args) > 1:
        code = " ".join(args[1:])
        run_eval(code)
        return
    if args[0].endswith(".mdl") or (os.path.exists(args[0]) and not args[0].startswith("-")):
        run_file(args[0])
        return
    print(f"未知参数: {args[0]}")
    print_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
