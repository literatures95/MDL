"""MDL 转换器 - Markdown AST 转换为 HTML / JSON / 纯文本"""

import json
import html as html_module
from ast_nodes import *


class HTMLConverter:
    """AST → HTML 转换器"""

    def convert(self, doc: DocumentNode, options: dict = None) -> str:
        """将文档转换为完整 HTML 页面"""
        opts = options or {}
        body_parts = []
        for child in doc.children:
            body_parts.append(self._convert_node(child))
        body_content = "\n".join(filter(None, body_parts))
        if opts.get("full_page", True):
            title = opts.get("title", "Markdown Document")
            css = opts.get("css", self._default_css())
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(title)}</title>
    <style>{css}</style>
</head>
<body class="markdown-body">
{body_content}
</body>
</html>"""
        return body_content

    def _default_css(self) -> str:
        return """
        .markdown-body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292f; max-width: 800px; margin: 0 auto; padding: 20px; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
        .markdown-body h1 { font-size: 2em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
        .markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
        .markdown-body p { margin-top: 0; margin-bottom: 16px; }
        .markdown-body code { background-color: rgba(175,184,193,0.2); border-radius: 6px; font-size: 85%; padding: 0.2em 0.4em; font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace; }
        .markdown-body pre { background-color: #f6f8fa; border-radius: 6px; padding: 16px; overflow-x: auto; font-size: 85%; line-height: 1.45; }
        .markdown-body pre code { background-color: transparent; padding: 0; border-radius: 0; white-space: pre; }
        .markdown-body blockquote { border-left: 0.25em solid #d0d7de; color: #57606a; padding: 0 1em; margin: 0 0 16px 0; }
        .markdown-body ul, .markdown-body ol { margin-top: 0; margin-bottom: 16px; padding-left: 2em; }
        .markdown-body li { margin-top: 0.25em; }
        .markdown-body table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
        .markdown-body table th, .markdown-body table td { border: 1px solid #d0d7de; padding: 6px 13px; }
        .markdown-body table th { background-color: #f6f8fa; font-weight: 600; }
        .markdown-body hr { height: 0.25em; border: none; background-color: #d0d7de; margin: 24px 0; }
        .markdown-body a { color: #0969da; text-decoration: none; }
        .markdown-body a:hover { text-decoration: underline; }
        .markdown-body img { max-width: 100%; box-sizing: content-box; }
        .markdown-body task-list-item { list-style-type: none; margin-left: -1.5em; }
        .markdown-body input[type=checkbox] { margin-right: 0.5em; }
        .markdown-body .critic-add { background-color: #d4edda; color: #155724; padding: 2px 4px; border-radius: 3px; text-decoration: none; }
        .markdown-body .critic-del { background-color: #f8d7da; color: #721c24; padding: 2px 4px; border-radius: 3px; text-decoration: line-through; }
        .markdown-body .critic-comment { cursor: help; color: #ffc107; font-weight: bold; }
        .markdown-body .critic-highlight { background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 3px; }
        .markdown-body .mermaid { border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin: 10px 0; background-color: #f9f9f9; }
        .markdown-body .plantuml { border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin: 10px 0; background-color: #f9f9f9; }
        """

    def _convert_node(self, node) -> str:
        dispatch = {
            NodeType.HEADING: self._to_html_heading,
            NodeType.PARAGRAPH: self._to_html_paragraph,
            NodeType.TEXT: self._to_html_text,
            NodeType.BOLD: self._to_html_bold,
            NodeType.ITALIC: self._to_html_italic,
            NodeType.BOLD_ITALIC: self._to_html_bold_italic,
            NodeType.STRIKETHROUGH: self._to_html_strikethrough,
            NodeType.CODE_INLINE: self._to_html_code_inline,
            NodeType.CODE_BLOCK: self._to_html_code_block,
            NodeType.BLOCKQUOTE: self._to_html_blockquote,
            NodeType.HORIZONTAL_RULE: self._to_html_hr,
            NodeType.UNORDERED_LIST: self._to_html_ul,
            NodeType.ORDERED_LIST: self._to_html_ol,
            NodeType.LIST_ITEM: self._to_html_li,
            NodeType.TASK_LIST: self._to_html_ul,
            NodeType.TASK_ITEM: self._to_html_task_item,
            NodeType.LINK: self._to_html_link,
            NodeType.IMAGE: self._to_html_image,
            NodeType.TABLE: self._to_html_table,
            NodeType.HTML_BLOCK: lambda n: n.html,
            NodeType.HTML_INLINE: lambda n: n.html,
            NodeType.LINE_BREAK: lambda n: "<br>",
            NodeType.SOFT_BREAK: lambda n: "\n",
            NodeType.SUPERSCRIPT: self._to_html_superscript,
            NodeType.SUBSCRIPT: self._to_html_subscript,
            NodeType.FOOTNOTE_REF: self._to_html_footnote_ref,
            NodeType.FOOTNOTE_DEF: self._to_html_footnote_def,
            NodeType.DEFINITION_LIST: self._to_html_definition_list,
            NodeType.DEFINITION_ITEM: self._to_html_definition_item,
            NodeType.MATH_INLINE: self._to_html_math_inline,
            NodeType.MATH_BLOCK: self._to_html_math_block,
            NodeType.MERMAID_DIAGRAM: self._to_html_mermaid_diagram,
            NodeType.PLANTUML_DIAGRAM: self._to_html_plantuml_diagram,
            NodeType.CRITIC_ADDITION: self._to_html_critic_addition,
            NodeType.CRITIC_DELETION: self._to_html_critic_deletion,
            NodeType.CRITIC_SUBSTITUTION: self._to_html_critic_substitution,
            NodeType.CRITIC_COMMENT: self._to_html_critic_comment,
            NodeType.CRITIC_HIGHLIGHT: self._to_html_critic_highlight,
        }
        func = dispatch.get(node.node_type)
        return func(node) if func else ""

    def _to_html_heading(self, node: HeadingNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<h{node.level}>{content}</h{node.level}>"

    def _to_html_paragraph(self, node: ParagraphNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<p>{content}</p>"

    def _to_html_text(self, node: TextNode) -> str:
        return html_module.escape(node.value)

    def _to_html_bold(self, node: BoldNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<strong>{content}</strong>"

    def _to_html_italic(self, node: ItalicNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<em>{content}</em>"

    def _to_html_bold_italic(self, node: BoldItalicNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<strong><em>{content}</em></strong>"

    def _to_html_strikethrough(self, node: StrikethroughNode) -> str:
        content = self._inline_to_html(node.content)
        return f"<del>{content}</del>"

    def _to_html_superscript(self, node: SuperscriptNode) -> str:
        return f"<sup>{html_module.escape(node.content)}</sup>"

    def _to_html_subscript(self, node: SubscriptNode) -> str:
        return f"<sub>{html_module.escape(node.content)}</sub>"

    def _to_html_code_inline(self, node: CodeInlineNode) -> str:
        return f"<code>{html_module.escape(node.code)}</code>"

    def _to_html_code_block(self, node: CodeBlockNode) -> str:
        escaped = html_module.escape(node.code)
        lang_attr = f' class="language-{node.language}"' if node.language else ""
        return f"<pre><code{lang_attr}>{escaped}</code></pre>"

    def _to_html_blockquote(self, node: BlockquoteNode) -> str:
        inner = "\n".join(self._convert_node(c) for c in (node.content or []) if c is not None)
        return f"<blockquote>{inner}</blockquote>" if inner.strip() else ""

    def _to_html_hr(self, node: HorizontalRuleNode) -> str:
        return "<hr>"

    def _to_html_ul(self, node) -> str:
        items_html = "\n".join(
            self._convert_node(item) for item in (getattr(node, "items", []))
        )
        tag = "ul"
        return f"<{tag}>\n{items_html}\n</{tag}>"

    def _to_html_ol(self, node: OrderedListNode) -> str:
        start_attr = f' start="{node.start}"' if node.start != 1 else ""
        items_html = "\n".join(self._convert_node(item) for item in node.items)
        return f"<ol{start_attr}>\n{items_html}\n</ol>"

    def _to_html_li(self, node: ListItemNode) -> str:
        content = self._inline_to_html(node.content)
        checked_str = ""
        if node.checked is not None:
            checked = 'checked=""' if node.checked else ""
            checked_str = f'<input type="checkbox" disabled {checked}> '
        return f"<li>{checked_str}{content}</li>"

    def _to_html_task_item(self, node: TaskItemNode) -> str:
        content = self._inline_to_html(node.content)
        checked = 'checked=""' if node.checked else ""
        return f'<li class="task-list-item"><input type="checkbox" disabled {checked}> {content}</li>'

    def _to_html_link(self, node: LinkNode) -> str:
        escaped_text = html_module.escape(node.text)
        title_attr = f' title="{html_module.escape(node.title)}"' if node.title else ""
        return f'<a href="{html_module.escape(node.url)}"{title_attr}>{escaped_text}</a>'

    def _to_html_image(self, node: ImageNode) -> str:
        alt = html_module.escape(node.alt)
        src = html_module.escape(node.src)
        title_attr = f' title="{html_module.escape(node.title)}"' if node.title else ""
        return f'<img src="{src}" alt="{alt}"{title_attr}>'

    def _to_html_table(self, node: TableNode) -> str:
        header_cells = "".join(f"<th>{html_module.escape(c.content)}</th>" for c in node.headers)
        header_row = f"<tr>{header_cells}</tr>"
        body_rows = ""
        for row in node.rows:
            cells = "".join(f"<td>{html_module.escape(c.content)}</td>" for c in row.cells)
            body_rows += f"<tr>{cells}</tr>\n"
        return f"<table>\n<thead>\n{header_row}\n</thead>\n<tbody>\n{body_rows}</tbody>\n</table>"

    def _to_html_footnote_ref(self, node: FootnoteRefNode) -> str:
        return f'<sup><a href="#fn-{node.ref_id}" id="fnref-{node.ref_id}">[{node.ref_id}]</a></sup>'

    def _to_html_footnote_def(self, node: FootnoteDefNode) -> str:
        content = self._inline_to_html(node.content)
        return f'<div id="fn-{node.ref_id}"><p>[{node.ref_id}] {content} <a href="#fnref-{node.ref_id}">↩</a></p></div>'

    def _to_html_definition_list(self, node: DefinitionListNode) -> str:
        items = []
        for item in node.items:
            items.append(self._to_html_definition_item(item))
        return f"<dl>\n{chr(10).join(items)}\n</dl>"

    def _to_html_definition_item(self, node: DefinitionItemNode) -> str:
        lines = [f"<dt>{html_module.escape(node.term)}</dt>"]
        for defn in node.definitions:
            lines.append(f"<dd>{html_module.escape(defn)}</dd>")
        return "\n".join(lines)

    def _to_html_math_inline(self, node: MathInlineNode) -> str:
        return f'<span class="math-inline">\\({node.formula}\\)</span>'

    def _to_html_math_block(self, node: MathBlockNode) -> str:
        return f'<div class="math-block">$$\n{node.formula}\n$$</div>'

    def _inline_to_html(self, nodes: list) -> str:
        if nodes is None:
            return ""
        parts = []
        for node in nodes:
            if isinstance(node, str):
                parts.append(html_module.escape(node))
            else:
                parts.append(self._convert_node(node))
        return "".join(parts)

    def _to_html_mermaid_diagram(self, node) -> str:
        """转换为 Mermaid 图表 HTML"""
        title_attr = f' title="{html_module.escape(node.title)}"' if node.title else ""
        return f'<div class="mermaid"{title_attr}>{html_module.escape(node.code)}</div>'

    def _to_html_plantuml_diagram(self, node) -> str:
        """转换为 PlantUML 图表 HTML"""
        title_attr = f' title="{html_module.escape(node.title)}"' if node.title else ""
        return f'<div class="plantuml"{title_attr}>{html_module.escape(node.code)}</div>'

    def _to_html_critic_addition(self, node) -> str:
        """转换为 CriticMarkup 添加 HTML"""
        content = self._inline_to_html(node.content)
        return f'<ins class="critic-add">{content}</ins>'

    def _to_html_critic_deletion(self, node) -> str:
        """转换为 CriticMarkup 删除 HTML"""
        content = self._inline_to_html(node.content)
        return f'<del class="critic-del">{content}</del>'

    def _to_html_critic_substitution(self, node) -> str:
        """转换为 CriticMarkup 替换 HTML"""
        remove_content = self._inline_to_html(node.remove_content)
        add_content = self._inline_to_html(node.add_content)
        return f'<del class="critic-del">{remove_content}</del><ins class="critic-add">{add_content}</ins>'

    def _to_html_critic_comment(self, node) -> str:
        """转换为 CriticMarkup 评论 HTML"""
        return f'<span class="critic-comment" title="{html_module.escape(node.comment)}">💬</span>'

    def _to_html_critic_highlight(self, node) -> str:
        """转换为 CriticMarkup 高亮 HTML"""
        content = self._inline_to_html(node.content)
        return f'<mark class="critic-highlight" title="{html_module.escape(node.comment)}">{content}</mark>'


class TextConverter:
    """AST → 纯文本转换器"""

    def convert(self, doc: DocumentNode) -> str:
        parts = []
        for child in doc.children:
            text = self._to_text(child)
            if text:
                parts.append(text)
                parts.append("\n\n")
        return "".join(parts).strip()

    def _to_text(self, node) -> str:
        if isinstance(node, HeadingNode):
            prefix = "#" * node.level
            content = self._inline_to_text(node.content)
            return f"{prefix} {content}"
        if isinstance(node, ParagraphNode):
            return self._inline_to_text(node.content) or node.raw_text
        if isinstance(node, TextNode):
            return node.value
        if isinstance(node, CodeBlockNode):
            return node.code
        if isinstance(node, CodeInlineNode):
            return node.code
        if isinstance(node, (BoldNode, ItalicNode, BoldItalicNode)):
            return self._inline_to_text(node.content)
        if isinstance(node, StrikethroughNode):
            return self._inline_to_text(node.content)
        if isinstance(node, BlockquoteNode):
            lines = [self._to_text(c) for c in (node.content or [])]
            return "\n".join(f"> {l}" for l in lines if l.strip())
        if isinstance(node, HorizontalRuleNode):
            return "---"
        if isinstance(node, LinkNode):
            return node.text
        if isinstance(node, ImageNode):
            return f"[图片: {node.alt}]"
        if isinstance(node, TableNode):
            rows = [[c.content for c in node.headers]]
            for r in node.rows:
                rows.append([c.content for c in r.cells])
            return "\n".join(" | ".join(row) for row in rows)
        if isinstance(node, (UnorderedListNode, OrderedListNode)):
            items = [self._to_text(i) for i in node.items]
            marker = getattr(node, "marker", "-")
            if isinstance(node, OrderedListNode):
                items = [f"{node.start + i}. {item}" for i, item in enumerate(items)]
            else:
                items = [f"{marker} {item}" for item in items]
            return "\n".join(items)
        if isinstance(node, TaskListNode):
            items = []
            for item in node.items:
                mark = "[x]" if item.checked else "[ ]"
                items.append(f"- {mark} {self._to_text(item)}")
            return "\n".join(items)
        if isinstance(node, (ListItemNode, TaskItemNode)):
            return self._inline_to_text(node.content)
        return ""

    def _inline_to_text(self, nodes: list) -> str:
        if nodes is None:
            return ""
        return "".join(self._to_text(n) for n in nodes)


class JSONConverter:
    """AST → JSON 转换器"""

    def convert(self, doc: DocumentNode, pretty: bool = True) -> str:
        data = doc.to_dict()
        indent = 2 if pretty else None
        return json.dumps(data, ensure_ascii=False, indent=indent)


def to_html(doc: DocumentNode, **kwargs) -> str:
    """便捷函数：转换为 HTML"""
    converter = HTMLConverter()
    return converter.convert(doc, kwargs)


def to_text(doc: DocumentNode) -> str:
    """便捷函数：转换为纯文本"""
    converter = TextConverter()
    return converter.convert(doc)


def to_json(doc: DocumentNode, pretty: bool = True) -> str:
    """便捷函数：转换为 JSON"""
    converter = JSONConverter()
    return converter.convert(doc, pretty)


def md_to_html(source: str, **kwargs) -> str:
    """便捷函数：Markdown 源文本 → HTML"""
    from md_parser import parse_markdown
    doc = parse_markdown(source)
    return to_html(doc, **kwargs)


def md_to_text(source: str) -> str:
    """便捷函数：Markdown 源文本 → 纯文本"""
    from md_parser import parse_markdown
    doc = parse_markdown(source)
    return to_text(doc)
