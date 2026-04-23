"""MDL REPL - 交互式命令行环境"""

from interpreter import Interpreter, MDLRuntimeError
from parser import parse
from ast_nodes import (
    CodeBlockNode, HeadingNode, OrderedListNode, ParagraphNode,
    TableNode, UnorderedListNode,
)


class REPL:
    """MDL 交互式解释器"""

    def __init__(self):
        self.interpreter = Interpreter()
        self.running = True
        self.history: list[str] = []
        self.prompt = "mdl> "
        self.continuation = "... "

    def start(self):
        """启动 REPL 循环"""
        self._print_banner()
        while self.running:
            try:
                line = input(self.prompt).strip()
                if not line:
                    continue
                if self._is_command(line):
                    self._handle_command(line)
                    continue
                code_block = self._collect_multiline(line)
                try:
                    result = self.interpreter.run_script(code_block)
                    if result is not None and not self._is_statement_only(code_block):
                        print(f"=> {result}")
                except MDLRuntimeError as e:
                    print(f"错误: {e}")
                except Exception as e:
                    print(f"异常: {type(e).__name__}: {e}")
            except EOFError:
                print("\n再见!")
                break
            except KeyboardInterrupt:
                print("\n已中断。输入 'quit' 退出")

    def _print_banner(self):
        """打印欢迎信息"""
        banner = """
╔══════════════════════════════════════════════╗
║         MDL - Markdown 操作语言 v1.0          ║
║     Markdown Operation & Analysis Language    ║
╠══════════════════════════════════════════════╣
║  输入 MDL 代码或命令，'help' 查看帮助          ║
║  'quit' 或 Ctrl+C 退出                        ║
╚══════════════════════════════════════════════╝
"""
        print(banner)

    def _is_command(self, line: str) -> bool:
        """判断是否为 REPL 命令"""
        commands = {"help", "quit", "exit", "clear", "cls", "vars", "docs",
                     "load", "save", "analyze", "tree", "tokens", "ast"}
        return line.lower().split()[0] in commands

    def _handle_command(self, line: str):
        """处理 REPL 命令"""
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        handlers = {
            "help": self._cmd_help,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
            "clear": self._cmd_clear,
            "cls": self._cmd_clear,
            "vars": self._cmd_vars,
            "docs": self._cmd_docs,
            "load": lambda a: self._quick_load(a),
            "save": lambda a: self._quick_save(a),
            "analyze": lambda a: self._quick_analyze(),
            "tree": lambda a: self._show_tree(),
            "tokens": lambda a: self._show_tokens(args),
            "ast": lambda a: self._show_ast(args),
        }
        handler = handlers.get(cmd)
        if handler:
            handler(args)

    def _cmd_help(self, args=""):
        """显示帮助信息"""
        help_text = """
┌─────────────────────────────────────────────┐
│              MDL 命令参考                     │
├─────────────────────────────────────────────┤
│ 文件操作:                                     │
│   load "path"              加载 Markdown 文件 │
│   save [doc] as "path"     保存文档           │
│                                             │
│ 文档查询:                                     │
│   doc.h1[0]               获取第1个一级标题   │
│   doc.h2                  获取所有二级标题    │
│   doc.p                   获取所有段落        │
│   doc.codeblock           获取所有代码块      │
│                                             │
│ 文档修改:                                     │
│   set doc.h1[0].text = "新标题"               │
│   insert after doc.h1[0]: "内容"              │
│   append: "追加的内容"                         │
│   remove doc.p[3]                             │
│                                             │
│ 格式转换:                                     │
│   convert doc to html save as "out.html"     │
│   convert doc to json                        │
│                                             │
│ 流程控制:                                     │
│   for item in list: ... end                  │
│   if condition: ... else: ... end            │
│   func name(params): ... end                 │
│                                             │
│ 内置函数:                                     │
│   len(), upper(), lower(), trim()            │
│   replace(), split(), join(), contains()     │
│   sort(), reverse(), unique(), range()       │
│   min(), max(), sum(), avg(), abs()          │
│   analyze(doc)                               │
└─────────────────────────────────────────────┘
"""
        print(help_text)

    def _cmd_quit(self, args=""):
        """退出 REPL"""
        print("再见! 👋")
        self.running = False

    def _cmd_clear(self, args=""):
        """清屏"""
        import os
        os.system("cls" if os.name == "nt" else "clear")

    def _cmd_vars(self, args=""):
        """显示当前变量"""
        vars_dict = self.interpreter.env.variables
        docs_dict = self.interpreter.env.documents
        print("\n--- 变量 ---")
        for k, v in vars_dict.items():
            val_str = str(v)[:50] + ("..." if len(str(v)) > 50 else "")
            print(f"  {k} = {val_str} ({type(v).__name__})")
        print("\n--- 文档 ---")
        for k, v in docs_dict.items():
            print(f"  {k}: {len(v.children)} 个元素")

    def _cmd_docs(self, args=""):
        """显示已加载文档列表"""
        docs = self.interpreter.env.documents
        if not docs:
            print("没有加载任何文档")
            return
        for name, doc in docs.items():
            print(f"\n📄 {name} ({len(doc.children)} 个元素):")
            for i, child in enumerate(doc.children):
                type_name = child.node_type.name
                extra = ""
                if hasattr(child, "raw_text") and child.raw_text:
                    extra = f": {child.raw_text[:40]}..."
                elif hasattr(child, "level"):
                    extra = f" (H{child.level})"
                print(f"  [{i}] {type_name}{extra}")

    def _quick_load(self, path: str):
        """快速加载文件"""
        path = path.strip().strip('"').strip("'")
        if not path:
            print("用法: load <文件路径>")
            return
        script = f'load "{path}"'
        self.interpreter.run_script(script)

    def _quick_save(self, args: str):
        """快速保存"""
        if not args:
            args = "doc"
        script = f'save {args}'
        self.interpreter.run_script(script)

    def _quick_analyze(self):
        """快速分析"""
        doc = self.interpreter.env.get_doc("doc")
        if not doc:
            print("请先加载文档 (load 命令)")
            return
        from analyzer import analyze
        result = analyze(doc)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))

    def _show_tree(self):
        """显示文档树形结构"""
        doc = self.interpreter.env.get_doc("doc")
        if not doc:
            print("请先加载文档")
            return
        self._print_tree(doc.children, indent=0)

    def _print_tree(self, nodes, indent: int):
        """递归打印树形结构"""
        prefix = "  " * indent
        for node in nodes:
            type_name = node.node_type.name
            extra = ""
            if isinstance(node, HeadingNode):
                extra = f" H{node.level}: {node.raw_text}"
            elif isinstance(node, ParagraphNode):
                preview = node.raw_text[:30] + ("..." if len(node.raw_text) > 30 else "")
                extra = f": {preview}"
            elif isinstance(node, CodeBlockNode):
                lang = node.language or "text"
                extra = f" ({lang}, {len(node.code)}字符)"
            elif isinstance(node, (UnorderedListNode, OrderedListNode)):
                extra = f" ({len(node.items)} 项)"
            elif isinstance(node, TableNode):
                extra = f" ({len(node.headers)}列 x {len(node.rows)}行)"
            print(f"{prefix}├─ {type_name}{extra}")

    def _show_tokens(self, source: str):
        """显示 Token 列表"""
        if not source:
            print("用法: tokens <表达式或代码>")
            return
        from lexer import tokenize
        tokens = tokenize(source)
        for tok in tokens:
            print(f"  {tok}")

    def _show_ast(self, source: str):
        """显示 AST 结构"""
        if not source:
            print("用法: ast <MDL代码>")
            return
        program = parse(source)
        import json
        print(json.dumps(program.to_dict(), ensure_ascii=False, indent=2))

    def _collect_multiline(self, first_line: str) -> str:
        """收集多行输入"""
        lines = [first_line]
        needs_more = self._needs_continuation(first_line)
        while needs_more:
            try:
                line = input(self.continuation)
                lines.append(line)
                needs_more = self._needs_continuation(line) or line.endswith(":")
            except EOFError:
                break
        return "\n".join(lines)

    def _needs_continuation(self, line: str) -> bool:
        """判断是否需要继续输入"""
        stripped = line.rstrip()
        keywords_needing_body = {"for", "if", "func", "else", "elif"}
        first_word = stripped.split()[0].lower() if stripped.split() else ""
        if first_word in keywords_needing_body and stripped.endswith(":"):
            return True
        open_parens = stripped.count("(") - stripped.count(")")
        open_brackets = stripped.count("[") - stripped.count("]")
        open_braces = stripped.count("{") - stripped.count("}")
        return open_parens > 0 or open_brackets > 0 or open_braces > 0

    def _is_statement_only(self, code: str) -> bool:
        """判断是否只是语句（无返回值）"""
        stmt_keywords = {"load", "save", "set", "insert", "append", "remove",
                         "convert", "for", "if", "func"}
        first_word = code.strip().split()[0].lower() if code.strip().split() else ""
        return first_word in stmt_keywords


def main_repl():
    """启动 REPL"""
    repl = REPL()
    repl.start()


if __name__ == "__main__":
    main_repl()
