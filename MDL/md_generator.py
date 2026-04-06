"""MDL Markdown 生成器 - 将 AST 完美还原为标准 Markdown 文本"""

import json
from ast_nodes import *


class MarkdownGenerator:
    """AST → Markdown 文本生成器"""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size

    def generate(self, doc: DocumentNode) -> str:
        """从文档节点生成完整 Markdown 文本"""
        parts = []
        for i, child in enumerate(doc.children):
            part = self._generate_node(child)
            if part:
                parts.append(part)
            if i < len(doc.children) - 1 and not isinstance(child, (HorizontalRuleNode, CodeBlockNode)):
                if not isinstance(child, (HTMLBlockNode,)):
                    parts.append("")
        return "\n".join(parts)

    def _generate_node(self, node) -> str:
        """根据节点类型分发到对应的生成方法"""
        dispatch = {
            NodeType.DOCUMENT: lambda n: self.generate(n),
            NodeType.HEADING: self._gen_heading,
            NodeType.PARAGRAPH: self._gen_paragraph,
            NodeType.TEXT: self._gen_text,
            NodeType.BOLD: self._gen_bold,
            NodeType.ITALIC: self._gen_italic,
            NodeType.BOLD_ITALIC: self._gen_bold_italic,
            NodeType.STRIKETHROUGH: self._gen_strikethrough,
            NodeType.SUPERSCRIPT: self._gen_superscript,
            NodeType.SUBSCRIPT: self._gen_subscript,
            NodeType.CODE_INLINE: self._gen_code_inline,
            NodeType.CODE_BLOCK: self._gen_code_block,
            NodeType.BLOCKQUOTE: self._gen_blockquote,
            NodeType.HORIZONTAL_RULE: self._gen_horizontal_rule,
            NodeType.UNORDERED_LIST: self._gen_unordered_list,
            NodeType.ORDERED_LIST: self._gen_ordered_list,
            NodeType.LIST_ITEM: self._gen_list_item,
            NodeType.TASK_LIST: self._gen_task_list,
            NodeType.TASK_ITEM: self._gen_task_item,
            NodeType.LINK: self._gen_link,
            NodeType.IMAGE: self._gen_image,
            NodeType.TABLE: self._gen_table,
            NodeType.HTML_BLOCK: self._gen_html_block,
            NodeType.HTML_INLINE: self._gen_html_inline,
            NodeType.LINE_BREAK: self._gen_line_break,
            NodeType.SOFT_BREAK: self._gen_soft_break,
            NodeType.FOOTNOTE_REF: self._gen_footnote_ref,
            NodeType.FOOTNOTE_DEF: self._gen_footnote_def,
            NodeType.DEFINITION_LIST: self._gen_definition_list,
            NodeType.DEFINITION_ITEM: self._gen_definition_item,
            NodeType.MATH_INLINE: self._gen_math_inline,
            NodeType.MATH_BLOCK: self._gen_math_block,
        }
        gen_func = dispatch.get(node.node_type)
        if gen_func:
            return gen_func(node)
        return ""

    def _gen_heading(self, node: HeadingNode) -> str:
        """生成标题 Markdown"""
        prefix = "#" * node.level
        content = self._generate_inline_content(node.content)
        return f"{prefix} {content}"

    def _gen_paragraph(self, node: ParagraphNode) -> str:
        """生成段落 Markdown"""
        if node.raw_text and not node.content:
            return node.raw_text
        return self._generate_inline_content(node.content)

    def _gen_text(self, node: TextNode) -> str:
        """生成纯文本"""
        return node.value

    def _gen_bold(self, node: BoldNode) -> str:
        """生成粗体文本"""
        content = self._generate_inline_content(node.content)
        return f"**{content}**"

    def _gen_italic(self, node: ItalicNode) -> str:
        """生成斜体文本"""
        content = self._generate_inline_content(node.content)
        return f"*{content}*"

    def _gen_bold_italic(self, node: BoldItalicNode) -> str:
        """生成粗斜体文本"""
        content = self._generate_inline_content(node.content)
        return f"***{content}***"

    def _gen_strikethrough(self, node: StrikethroughNode) -> str:
        """生成删除线文本"""
        content = self._generate_inline_content(node.content)
        return f"~~{content}~~"

    def _gen_superscript(self, node: SuperscriptNode) -> str:
        """生成上标文本"""
        return f"^{node.content}^"

    def _gen_subscript(self, node: SubscriptNode) -> str:
        """生成下标文本"""
        return f"~{node.content}~"

    def _gen_code_inline(self, node: CodeInlineNode) -> str:
        """生成行内代码"""
        return f"`{node.code}`"

    def _gen_code_block(self, node: CodeBlockNode) -> str:
        """生成代码块"""
        if node.fenced:
            fence = "```"
            lang = node.language or ""
            return f"{fence}{lang}\n{node.code}{fence}"
        else:
            lines = node.code.split("\n")
            indented = ["    " + line for line in lines]
            return "\n".join(indented)

    def _gen_blockquote(self, node: BlockquoteNode) -> str:
        """生成引用块"""
        lines = []
        for child in node.content:
            child_md = self._generate_node(child)
            if child_md:
                for sub_line in child_md.split("\n"):
                    lines.append(f"> {sub_line}")
        return "\n".join(lines)

    def _gen_horizontal_rule(self, node: HorizontalRuleNode) -> str:
        """生成分隔线"""
        return node.style

    def _gen_unordered_list(self, node: UnorderedListNode) -> str:
        """生成无序列表"""
        lines = []
        for i, item in enumerate(node.items):
            item_md = self._gen_list_item_with_indent(item, marker=node.marker, level=0, index=i)
            lines.extend(item_md)
        return "\n".join(lines)

    def _gen_ordered_list(self, node: OrderedListNode) -> str:
        """生成有序列表"""
        lines = []
        for i, item in enumerate(node.items):
            num = node.start + i
            item_md = self._gen_list_item_with_indent(item, marker=f"{num}.", level=0, index=i)
            lines.extend(item_md)
        return "\n".join(lines)

    def _gen_list_item(self, node: ListItemNode) -> str:
        """生成列表项"""
        content = self._generate_inline_content(node.content)
        if node.checked is True:
            return f"- [x] {content}"
        elif node.checked is False:
            return f"- [ ] {content}"
        return f"- {content}"

    def _gen_task_list(self, node: TaskListNode) -> str:
        """生成任务列表"""
        lines = []
        for i, item in enumerate(node.items):
            item_md = self._gen_task_item_with_indent(item, level=0, index=i)
            lines.extend(item_md)
        return "\n".join(lines)

    def _gen_task_item(self, node: TaskItemNode) -> str:
        """生成任务项"""
        checkbox = "[x]" if node.checked else "[ ]"
        content = self._generate_inline_content(node.content)
        return f"- {checkbox} {content}"

    def _gen_link(self, node: LinkNode) -> str:
        """生成链接"""
        if node.title:
            return f"[{node.text}]({node.url} \"{node.title}\")"
        return f"[{node.text}]({node.url})"

    def _gen_image(self, node: ImageNode) -> str:
        """生成图片"""
        if node.title:
            return f"![{node.alt}]({node.src} \"{node.title}\")"
        return f"![{node.alt}]({node.src})"

    def _gen_table(self, node: TableNode) -> str:
        """生成表格"""
        header_cells = "|".join(
            self._format_table_cell(c.content, c.alignment) for c in node.headers
        )
        separator_parts = []
        for align in node.alignments:
            if align == "center":
                separator_parts.append(":---:")
            elif align == "right":
                separator_parts.append("---:")
            else:
                separator_parts.append("---")
        separator = "|" + "|".join(separator_parts) + "|"
        lines = [f"|{header_cells}|", separator]
        for row in node.rows:
            cells = "|".join(self._format_table_cell(c.content) for c in row.cells)
            lines.append(f"|{cells}|")
        return "\n".join(lines)

    def _format_table_cell(self, content: str, alignment: str = "") -> str:
        """格式化表格单元格"""
        if alignment == "center":
            return f" {content} "
        elif alignment == "right":
            return f" {content}"
        return f"{content} "

    def _gen_html_block(self, node: HTMLBlockNode) -> str:
        """生成 HTML 块"""
        return node.html

    def _gen_html_inline(self, node: HTMLInlineNode) -> str:
        """生成行内 HTML"""
        return node.html

    def _gen_line_break(self, node: LineBreakNode) -> str:
        """生成硬换行"""
        return "  \n"

    def _gen_soft_break(self, node: SoftBreakNode) -> str:
        """生成软换行"""
        return "\n"

    def _gen_footnote_ref(self, node: FootnoteRefNode) -> str:
        """生成脚注引用"""
        return f"[^{node.ref_id}]"

    def _gen_footnote_def(self, node: FootnoteDefNode) -> str:
        """生成脚注定义"""
        content = self._generate_inline_content(node.content)
        return f"[^{node.ref_id}]: {content}"

    def _gen_definition_list(self, node: DefinitionListNode) -> str:
        """生成定义列表"""
        lines = []
        for item in node.items:
            lines.append(self._gen_definition_item(item))
        return "\n".join(lines)

    def _gen_definition_item(self, node: DefinitionItemNode) -> str:
        """生成定义项"""
        lines = [node.term]
        for defn in node.definitions:
            lines.append(f": {defn}")
        return "\n".join(lines)

    def _gen_math_inline(self, node: MathInlineNode) -> str:
        """生成行内数学公式"""
        return f"${node.formula}$"

    def _gen_math_block(self, node: MathBlockNode) -> str:
        """生成块级数学公式"""
        return f"$$\n{node.formula}\n$$"

    def _generate_inline_content(self, nodes: list) -> str:
        """将行内节点列表转换为纯文本"""
        if nodes is None:
            return ""
        parts = []
        for node in nodes:
            if isinstance(node, str):
                parts.append(node)
            else:
                parts.append(self._generate_node(node))
        return "".join(parts)

    def _gen_list_item_with_indent(self, item, marker: str = "-", level: int = 0, index: int = 0) -> list[str]:
        """生成带缩进的列表项"""
        indent = "  " * level
        content = self._generate_inline_content(item.content)
        checked_str = ""
        if isinstance(item, ListItemNode) and item.checked is not None:
            checked_str = "[x] " if item.checked else "[ ] "
        elif isinstance(item, TaskItemNode):
            checked_str = "[x] " if item.checked else "[ ] "
        main_line = f"{indent}{marker} {checked_str}{content}"
        result = [main_line]
        if hasattr(item, "content") and isinstance(item.content, list):
            for child in item.content:
                if isinstance(child, (UnorderedListNode, OrderedListNode, TaskListNode)):
                    sub_lines = self._generate_node(child).split("\n")
                    for sl in sub_lines:
                        result.append(f"  {indent}{sl}")
        return result

    def _gen_task_item_with_indent(self, item, level: int = 0, index: int = 0) -> list[str]:
        """生成带缩进的任务项"""
        indent = "  " * level
        checkbox = "[x]" if item.checked else "[ ]"
        content = self._generate_inline_content(item.content)
        main_line = f"{indent}- {checkbox} {content}"
        return [main_line]


def generate_markdown(doc: DocumentNode) -> str:
    """便捷函数：从 AST 生成 Markdown 文本"""
    generator = MarkdownGenerator()
    return generator.generate(doc)


def generate_node(node) -> str:
    """便捷函数：从单个节点生成 Markdown"""
    generator = MarkdownGenerator()
    return generator._generate_node(node)


def generate_inline(nodes: list) -> str:
    """便捷函数：从行内节点列表生成文本"""
    generator = MarkdownGenerator()
    return generator._generate_inline_content(nodes)
