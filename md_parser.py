"""MDL Markdown 解析引擎 - 完美解析所有 Markdown 元素为 AST"""

import re
from ast_nodes import *


class MDParseError(Exception):
    """Markdown 解析错误"""
    pass


class MarkdownParser:
    """Markdown 文本 → AST 解析器 - 支持完整 GFM 语法"""

    def __init__(self, source: str = ""):
        self.source = source
        self.lines: list[str] = []
        self.pos = 0
        if source:
            self.lines = source.split("\n")
            self._normalize_lines()

    def _normalize_lines(self):
        """标准化行尾符"""
        self.lines = [line.rstrip("\r") for line in self.lines]

    def _current_line(self) -> str:
        if 0 <= self.pos < len(self.lines):
            return self.lines[self.pos]
        return ""

    def _peek_line(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if 0 <= idx < len(self.lines):
            return self.lines[idx]
        return ""

    def _advance(self) -> str:
        line = self._current_line()
        self.pos += 1
        return line

    def _at_end(self) -> bool:
        return self.pos >= len(self.lines)

    def parse(self, source: str = None) -> DocumentNode:
        """解析 Markdown 源文本为 AST 文档节点"""
        if source is not None:
            self.source = source
            self.lines = source.split("\n")
            self._normalize_lines()
            self.pos = 0
        doc = DocumentNode()
        while not self._at_end():
            node = self._parse_block()
            if node:
                doc.children.append(node)
        return doc

    def _parse_block(self):
        """解析块级元素"""
        line = self._current_line().rstrip()
        stripped = line.lstrip()
        if not stripped and not self._at_end():
            self.pos += 1
            return None
        if self._is_atx_heading(stripped):
            return self._parse_atx_heading()
        if self._is_setext_heading():
            return self._parse_setext_heading()
        if self._is_math_block(stripped):
            return self._parse_math_block()
        if self._is_footnote_def(stripped):
            return self._parse_footnote_def()
        if self._is_definition_list(stripped):
            return self._parse_definition_list()
        if self._is_fenced_code_block(stripped):
            return self._parse_fenced_code_block()
        if self._is_indented_code_block(stripped):
            return self._parse_indented_code_block()
        if self._is_horizontal_rule(stripped):
            return self._parse_horizontal_rule()
        if self._is_html_block(stripped):
            return self._parse_html_block()
        if self._is_table(stripped):
            return self._parse_table()
        if self._is_blockquote(stripped):
            return self._parse_blockquote()
        if self._is_list_item(stripped):
            return self._parse_list()
        return self._parse_paragraph()

    def _is_atx_heading(self, line: str) -> bool:
        """判断是否为 ATX 标题 (# 标题)"""
        match = re.match(r"^(#{1,6})\s", line)
        return bool(match) and not line.startswith("###")

    def _parse_atx_heading(self) -> HeadingNode:
        """解析 ATX 标题"""
        line = self._current_line().rstrip()
        match = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", line)
        level = len(match.group(1))
        raw_text = match.group(2).strip()
        content = self._parse_inline(raw_text)
        self.pos += 1
        heading = HeadingNode(level=level, content=content, raw_text=raw_text, line=self.pos)
        return heading

    def _is_setext_heading(self) -> bool:
        """判断是否为 Setext 标题 (下划线标题)"""
        if self.pos + 1 >= len(self.lines):
            return False
        next_line = self.lines[self.pos + 1].strip()
        if re.match(r"^={3,}$", next_line) or re.match(r"^-{3,}$", next_line):
            current = self._current_line().strip()
            return bool(current and not current.startswith("#") and not current.startswith(">") and not current.startswith("-") and not current.startswith("*"))
        return False

    def _parse_setext_heading(self) -> HeadingNode:
        """解析 Setext 标题"""
        text_line = self._current_line().rstrip()
        underline = self.lines[self.pos + 1].strip()
        level = 1 if underline.startswith("=") else 2
        content = self._parse_inline(text_line.strip())
        heading = HeadingNode(level=level, content=content, raw_text=text_line.strip(), line=self.pos + 1)
        self.pos += 2
        return heading

    def _is_fenced_code_block(self, line: str) -> bool:
        """判断是否为围栏代码块 (``` 或 ~~~)"""
        return bool(re.match(r"^(`{3,}|~{3,})", line))

    def _parse_fenced_code_block(self) -> CodeBlockNode:
        """解析围栏代码块"""
        start_line = self._current_line()
        fence_match = re.match(r"^(`{3,}|~{3,})\s*(\w*)", start_line)
        fence = fence_match.group(1)
        language = fence_match.group(2).lower() if fence_match.group(2) else ""
        code_lines = []
        self.pos += 1
        while not self._at_end():
            line = self._current_line()
            if re.match(re.escape(fence) + r"*\s*$", line):
                self.pos += 1
                break
            code_lines.append(line)
            self.pos += 1
        code_text = "\n".join(code_lines)
        return CodeBlockNode(code=code_text, language=language, fenced=True, line=self.pos - len(code_lines))

    def _is_indented_code_block(self, line: str) -> bool:
        """判断是否为缩进代码块（4个空格或1个制表符）"""
        return bool(re.match(r"^(\t| {4})", line)) and not self._is_list_item(line)

    def _parse_indented_code_block(self) -> CodeBlockNode:
        """解析缩进代码块"""
        code_lines = []
        while not self._at_end():
            line = self._current_line()
            if re.match(r"^(\t| {4})", line):
                code_lines.append(re.sub(r"^(\t| {1,4})", "", line))
                self.pos += 1
            elif line.strip() == "":
                code_lines.append("")
                self.pos += 1
            else:
                break
        code_text = "\n".join(code_lines).rstrip("\n")
        return CodeBlockNode(code=code_text, language="", fenced=False, line=self.pos - len(code_lines))

    def _is_math_block(self, line: str) -> bool:
        """判断是否为块级数学公式 $$...$$"""
        return line.strip().startswith("$$")

    def _parse_math_block(self) -> MathBlockNode:
        """解析块级数学公式"""
        formula_lines = []
        self.pos += 1
        while not self._at_end():
            line = self._current_line()
            if line.strip() == "$$":
                self.pos += 1
                break
            formula_lines.append(line.rstrip())
            self.pos += 1
        formula = "\n".join(formula_lines)
        return MathBlockNode(formula=formula, line=self.pos - len(formula_lines))

    def _is_footnote_def(self, line: str) -> bool:
        """判断是否为脚注定义 [^id]: 内容"""
        return bool(re.match(r"^\[\^[^\]]+\]:\s", line))

    def _parse_footnote_def(self) -> FootnoteDefNode:
        """解析脚注定义"""
        line = self._current_line()
        match = re.match(r"^\[\^([^\]]+)\]:\s*(.*)$", line)
        ref_id = match.group(1)
        first_line = match.group(2)
        self.pos += 1
        content_lines = [first_line] if first_line else []
        while not self._at_end():
            next_line = self._current_line()
            if next_line.startswith("    ") or next_line.startswith("\t"):
                content_lines.append(next_line.strip())
                self.pos += 1
            else:
                break
        content_text = "\n".join(content_lines)
        content = self._parse_inline(content_text)
        return FootnoteDefNode(ref_id=ref_id, content=content, line=self.pos)

    def _is_definition_list(self, line: str) -> bool:
        """判断是否为定义列表（下一行以 : 开头）"""
        if self.pos + 1 >= len(self.lines):
            return False
        next_line = self.lines[self.pos + 1].lstrip()
        return bool(re.match(r"^:\s", next_line))

    def _parse_definition_list(self) -> DefinitionListNode:
        """解析定义列表"""
        items = []
        while not self._at_end():
            line = self._current_line()
            stripped = line.lstrip()
            if re.match(r"^:\s", stripped):
                if items:
                    last_item = items[-1]
                    last_item.definitions.append(stripped[1:].strip())
                self.pos += 1
                continue
            if not stripped:
                self.pos += 1
                if self._at_end() or not self._is_definition_list(self._current_line().lstrip()):
                    break
                continue
            next_idx = self.pos + 1
            if next_idx < len(self.lines):
                next_line = self.lines[next_idx].lstrip()
                if re.match(r"^:\s", next_line):
                    term = stripped
                    items.append(DefinitionItemNode(term=term, definitions=[]))
                    self.pos += 1
                    continue
            break
        return DefinitionListNode(items=items, line=self.pos)

    def _is_horizontal_rule(self, line: str) -> bool:
        """判断是否为分隔线"""
        stripped = line.strip()
        return bool(
            re.match(r"^(\*\s*){3,}\s*$", stripped)
            or re.match(r"^(-\s*){3,}\s*$", stripped)
            or re.match(r"(_\s*){3,}\s*$", stripped)
        )

    def _parse_horizontal_rule(self) -> HorizontalRuleNode:
        """解析分隔线"""
        line = self._current_line().strip()
        style = "***"
        if line.startswith("---"):
            style = "---"
        elif line.startswith("___"):
            style = "___"
        self.pos += 1
        return HorizontalRuleNode(style=style, line=self.pos)

    def _is_html_block(self, line: str) -> bool:
        """判断是否为 HTML 块"""
        stripped = line.strip()
        html_patterns = [
            r"^<script", r"^</script", r"^<style", r"^</style",
            r"^<pre", r"^</pre", r"^<!--", r"^<div",
            "^<p\\b", "^</p>", "^<h[1-6]", "^</h[1-6]",
            "^<table", "^</table>", "^<ul", "^</ul>",
            "^<ol", "^</ol>", "^<li", "^</li>",
            "^<blockquote", "^</blockquote>", "^<hr",
            "^<details", "^<summary",
        ]
        return any(re.match(p, stripped, re.IGNORECASE) for p in html_patterns)

    def _parse_html_block(self) -> HTMLBlockNode:
        """解析 HTML 块"""
        html_lines = []
        tag_match = re.match(r"<(\w+)", self._current_line().strip())
        tag_name = tag_match.group(1).lower() if tag_match else "div"
        depth = 1
        while not self._at_end() and depth > 0:
            line = self._current_line()
            open_tags = len(re.findall(rf"<{re.escape(tag_name)}\b", line, re.IGNORECASE))
            close_tags = len(re.findall(rf"</{re.escape(tag_name)}\s*>", line, re.IGNORECASE))
            depth += open_tags - close_tags
            html_lines.append(line)
            self.pos += 1
            if depth <= 0:
                break
        html_text = "\n".join(html_lines)
        return HTMLBlockNode(html=html_text, tag=tag_name, line=self.pos - len(html_lines))

    def _is_table(self, line: str) -> bool:
        """判断是否为表格"""
        stripped = line.strip()
        if "|" not in stripped:
            return False
        if self.pos + 1 < len(self.lines):
            next_line = self.lines[self.pos + 1].strip()
            if re.match(r"^[\|\s\-:]+$", next_line) and "---" in next_line:
                return True
        return False

    def _parse_table(self) -> TableNode:
        """解析表格"""
        header_line = self._current_line()
        self.pos += 1
        sep_line = self._current_line()
        self.pos += 1
        headers_raw = self._split_table_row(header_line)
        alignments = self._parse_table_alignments(sep_line)
        headers = [TableCellNode(content=h.strip(), alignment=a) for h, a in zip(headers_raw, alignments)]
        rows = []
        while not self._at_end():
            line = self._current_line().strip()
            if not line or "|" not in line:
                break
            cells_raw = self._split_table_row(line)
            row_cells = [TableCellNode(content=c.strip()) for c in cells_raw]
            rows.append(TableRowNode(cells=row_cells))
            self.pos += 1
        header_row = TableRowNode(cells=headers, is_header=True)
        return TableNode(headers=headers, rows=rows, alignments=alignments, line=self.pos - len(rows) - 2)

    def _split_table_row(self, line: str) -> list[str]:
        """分割表格行"""
        parts = line.split("|")
        return [p for p in parts if p.strip() or True]

    def _parse_table_alignments(self, sep_line: str) -> list[str]:
        """解析表格对齐方式"""
        cells = sep_line.split("|")
        alignments = []
        for cell in cells:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append("center")
            elif cell.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")
        return alignments

    def _is_blockquote(self, line: str) -> bool:
        """判断是否为引用块"""
        return line.startswith(">")

    def _parse_blockquote(self) -> BlockquoteNode:
        """解析引用块"""
        quote_lines = []
        level = 0
        while not self._at_end():
            line = self._current_line()
            match = re.match(r"^(>+)\s?(.*)$", line)
            if match:
                current_level = len(match.group(1))
                if level == 0:
                    level = current_level
                quote_lines.append(match.group(2))
                self.pos += 1
            elif line.strip() == "" and quote_lines:
                quote_lines.append("")
                self.pos += 1
            else:
                break
        quote_text = "\n".join(quote_lines)
        inner_parser = MarkdownParser(quote_text)
        inner_doc = inner_parser.parse()
        return BlockquoteNode(content=inner_doc.children, level=level, line=self.pos - len(quote_lines))

    def _is_list_item(self, line: str) -> bool:
        """判断是否为列表项"""
        unordered_pattern = r"^(\s*)([-*+])\s+"
        ordered_pattern = r"^(\s*)(\d+)\.(\s|\))+\s*"
        task_pattern = r"^(\s*)([-*+])\s+\[[ xX]\]\s+"
        return (
            bool(re.match(unordered_pattern, line))
            or bool(re.match(ordered_pattern, line))
            or bool(re.match(task_pattern, line))
        )

    def _get_list_indent(self, line: str) -> int:
        """获取列表缩进级别"""
        match = re.match(r"^(\s*)", line)
        return len(match.group(1)) if match else 0

    def _parse_list(self):
        """解析列表（有序/无序/任务列表）"""
        first_line = self._current_line()
        task_match = re.match(r"^(\s*)([-*+])\s+\[([ xX])\]\s+(.*)$", first_line)
        unordered_match = re.match(r"^(\s*)([-*+])\s+(.*)$", first_line)
        ordered_match = re.match(r"^(\s*)(\d+)\.(\s|\))+\s*(.*)$", first_line)
        is_task = bool(task_match)
        items = []
        marker = ""
        start_num = 1
        base_indent = self._get_list_indent(first_line)
        if task_match:
            marker = task_match.group(2)
        elif unordered_match:
            marker = unordered_match.group(2)
        elif ordered_match:
            start_num = int(ordered_match.group(2))
        while not self._at_end():
            line = self._current_line()
            current_indent = self._get_list_indent(line)
            if current_indent < base_indent and line.strip():
                break
            if not line.strip():
                if items and self._peek_line(1).strip():
                    self.pos += 1
                    continue
                break
            task_m = re.match(r"^(\s*)([-*+])\s+\[([ xX])\]\s+(.*)$", line)
            unord_m = re.match(r"^(\s*)([-*+])\s+(.*)$", line)
            ord_m = re.match(r"^(\s*)(\d+)\.(\s|\))+\s*(.*)$", line)
            item_content = ""
            checked = None
            if task_m:
                checked = task_m.group(3).lower() == "x"
                item_content = task_m.group(4)
            elif unord_m:
                item_content = unord_m.group(3)
            elif ord_m:
                item_content = ord_m.group(4)
            sub_lines = [item_content]
            self.pos += 1
            while not self._at_end():
                next_line = self._current_line()
                next_indent = self._get_list_indent(next_line)
                if next_line.strip() and next_indent > base_indent + 2:
                    sub_lines.append(next_line.lstrip())
                    self.pos += 1
                elif not next_line.strip():
                    peek = self._peek_line(1)
                    if self._get_list_indent(peek) > base_indent:
                        sub_lines.append("")
                        self.pos += 1
                    else:
                        break
                else:
                    break
            full_content = "\n".join(sub_lines)
            inline_nodes = self._parse_inline(full_content)
            if is_task:
                items.append(TaskItemNode(content=inline_nodes, checked=bool(checked)))
            else:
                items.append(ListItemNode(content=inline_nodes, checked=checked))
        if is_task:
            return TaskListNode(items=items, line=self.pos - len(items))
        if ordered_match:
            return OrderedListNode(items=items, start=start_num, marker=".", line=self.pos - len(items))
        return UnorderedListNode(items=items, marker=marker, line=self.pos - len(items))

    def _parse_paragraph(self) -> ParagraphNode:
        """解析段落"""
        lines = []
        while not self._at_end():
            line = self._current_line().rstrip()
            stripped = line.strip()
            if not stripped:
                break
            if self._is_atx_heading(stripped) or self._is_setext_heading():
                break
            if self._is_fenced_code_block(stripped) or self._is_horizontal_rule(stripped):
                break
            if self._is_html_block(stripped):
                break
            if self._is_table(stripped):
                break
            if self._is_blockquote(stripped):
                break
            if self._is_list_item(stripped) and not lines:
                break
            lines.append(stripped)
            self.pos += 1
        raw_text = " ".join(lines)
        content = self._parse_inline(raw_text)
        return ParagraphNode(content=content, raw_text=raw_text, line=self.pos - len(lines))

    def _parse_inline(self, text: str) -> list:
        """解析行内元素"""
        nodes = []
        pos = 0
        length = len(text)
        while pos < length:
            remaining = text[pos:]
            bold_italic_match = re.match(r"\*\*\*(.+?)\*\*\*", remaining)
            if bold_italic_match:
                inner = self._parse_inline(bold_italic_match.group(1))
                nodes.append(BoldItalicNode(content=inner))
                pos += bold_italic_match.end()
                continue
            bold_match = re.match(r"\*\*(.+?)\*\*", remaining)
            if bold_match:
                inner = self._parse_inline(bold_match.group(1))
                nodes.append(BoldNode(content=inner))
                pos += bold_match.end()
                continue
            italic_match = re.match(r"\*(.+?)\*", remaining)
            if italic_match and not remaining.startswith("**"):
                inner = self._parse_inline(italic_match.group(1))
                nodes.append(ItalicNode(content=inner))
                pos += italic_match.end()
                continue
            strike_match = re.match(r"~~(.+?)~~", remaining)
            if strike_match:
                inner = self._parse_inline(strike_match.group(1))
                nodes.append(StrikethroughNode(content=inner))
                pos += strike_match.end()
                continue
            superscript_match = re.match(r"\^([^^]+?)\^", remaining)
            if superscript_match:
                nodes.append(SuperscriptNode(content=superscript_match.group(1)))
                pos += superscript_match.end()
                continue
            subscript_match = re.match(r"~([^~]+?)~", remaining)
            if subscript_match and not remaining.startswith("~~"):
                nodes.append(SubscriptNode(content=subscript_match.group(1)))
                pos += subscript_match.end()
                continue
            math_inline_match = re.match(r"\$([^$\n]+?)\$", remaining)
            if math_inline_match:
                nodes.append(MathInlineNode(formula=math_inline_match.group(1)))
                pos += math_inline_match.end()
                continue
            code_match = re.match(r"`([^`]+)`", remaining)
            if code_match:
                nodes.append(CodeInlineNode(code=code_match.group(1)))
                pos += code_match.end()
                continue
            footnote_ref_match = re.match(r"\[\^([^\]]+)\]", remaining)
            if footnote_ref_match:
                nodes.append(FootnoteRefNode(ref_id=footnote_ref_match.group(1)))
                pos += footnote_ref_match.end()
                continue
            image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", remaining)
            if image_match:
                title_match = re.match(r'!\[([^\]]*)\]\(([^)\s]+)\s+"([^"]+)"\)', remaining)
                if title_match:
                    nodes.append(ImageNode(alt=title_match.group(1), src=title_match.group(2), title=title_match.group(3)))
                    pos += title_match.end()
                else:
                    nodes.append(ImageNode(alt=image_match.group(1), src=image_match.group(2)))
                    pos += image_match.end()
                continue
            link_match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", remaining)
            if link_match:
                title_match = re.match(r'\[([^\]]+)\]\(([^)\s]+)\s+"([^"]+)"\)', remaining)
                if title_match:
                    nodes.append(LinkNode(text=title_match.group(1), url=title_match.group(2), title=title_match.group(3)))
                    pos += title_match.end()
                else:
                    nodes.append(LinkNode(text=link_match.group(1), url=link_match.group(2)))
                    pos += link_match.end()
                continue
            auto_link_match = re.match(r"<(https?://[^>]+)>", remaining)
            if auto_link_match:
                nodes.append(LinkNode(text=auto_link_match.group(1), url=auto_link_match.group(1)))
                pos += auto_link_match.end()
                continue
            html_inline_match = re.match(r"<(/?\w+[^>]*)>", remaining)
            if html_inline_match:
                nodes.append(HTMLInlineNode(html=html_inline_match.group(0)))
                pos += html_inline_match.end()
                continue
            hard_break_match = re.match(r"  \n|\\\n", remaining)
            if hard_break_match:
                nodes.append(LineBreakNode())
                pos += hard_break_match.end()
                continue
            escape_match = re.match(r"\\([\\`*_{}[]()#+\-.!|~^$])", remaining)
            if escape_match:
                nodes.append(TextNode(value=escape_match.group(1)))
                pos += escape_match.end()
                continue
            nodes.append(TextNode(value=text[pos]))
            pos += 1
        return nodes

    def get_element_count(self) -> dict:
        """统计文档中各元素数量"""
        doc = self.parse()
        counts = {}
        for child in doc.children:
            type_name = child.node_type.name
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def get_structure(self) -> list[dict]:
        """获取文档结构大纲"""
        doc = self.parse()
        structure = []
        for child in doc.children:
            info = {"type": child.node_type.name, "line": child.line}
            if isinstance(child, HeadingNode):
                info["level"] = child.level
                info["text"] = child.raw_text
            elif isinstance(child, ParagraphNode):
                info["preview"] = child.raw_text[:80] + ("..." if len(child.raw_text) > 80 else "")
            structure.append(info)
        return structure


def parse_markdown(source: str) -> DocumentNode:
    """便捷函数：解析 Markdown 文本为 AST"""
    parser = MarkdownParser(source)
    return parser.parse()


def parse_file(filepath: str, encoding: str = "utf-8") -> DocumentNode:
    """便捷函数：从文件解析 Markdown"""
    with open(filepath, "r", encoding=encoding) as f:
        source = f.read()
    return parse_markdown(source)


def split_document(doc: DocumentNode) -> dict:
    """拆分文档为各类型元素的集合"""
    result = {
        "headings": [],
        "paragraphs": [],
        "code_blocks": [],
        "lists": [],
        "blockquotes": [],
        "tables": [],
        "images": [],
        "links": [],
        "horizontal_rules": [],
        "html_blocks": [],
        "other": [],
    }
    for child in doc.children:
        if isinstance(child, HeadingNode):
            result["headings"].append(child)
        elif isinstance(child, ParagraphNode):
            result["paragraphs"].append(child)
        elif isinstance(child, CodeBlockNode):
            result["code_blocks"].append(child)
        elif isinstance(child, (UnorderedListNode, OrderedListNode, TaskListNode)):
            result["lists"].append(child)
        elif isinstance(child, BlockquoteNode):
            result["blockquotes"].append(child)
        elif isinstance(child, TableNode):
            result["tables"].append(child)
        elif isinstance(child, HTMLBlockNode):
            result["html_blocks"].append(child)
        elif isinstance(child, HorizontalRuleNode):
            result["horizontal_rules"].append(child)
        else:
            result["other"].append(child)
    for child in doc.children:
        _extract_links_images(child, result)
    return result


def _extract_links_images(node, result: dict):
    """递归提取链接和图片"""
    if isinstance(node, LinkNode):
        result["links"].append(node)
    elif isinstance(node, ImageNode):
        result["images"].append(node)
    elif hasattr(node, "content"):
        content = node.content
        if isinstance(content, list):
            for child in content:
                _extract_links_images(child, result)
