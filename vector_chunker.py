"""MDL 语义分块器 - 基于 AST 的 Markdown 语义分块"""

import uuid
from typing import Optional
from dataclasses import dataclass, field

from ast_nodes import (
    DocumentNode, HeadingNode, ParagraphNode, TextNode, CodeBlockNode,
    BlockquoteNode, UnorderedListNode, OrderedListNode, TableNode,
    ListItemNode, TaskItemNode, HorizontalRuleNode,
)
from md_generator import generate_markdown
from md_parser import parse_markdown


@dataclass
class Chunk:
    """单个语义块"""
    id: str = ""
    text: str = ""
    markdown: str = ""
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list] = None


@dataclass
class ChunkerConfig:
    """分块器配置"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    respect_headings: bool = True
    min_chunk_size: int = 50


class MarkdownChunker:
    """基于 AST 的 Markdown 语义分块器"""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()

    def chunk_document(self, doc: DocumentNode, source_path: str = "") -> list[Chunk]:
        """从 DocumentNode AST 分块"""
        sections = self._build_sections(doc.children)
        chunks = []
        for section in sections:
            section_chunks = self._split_section(section)
            for i, c in enumerate(section_chunks):
                c.metadata["source_path"] = source_path
                c.metadata["section_index"] = i
            chunks.extend(section_chunks)
        return chunks

    def chunk_file(self, file_path: str) -> list[Chunk]:
        """读取文件并分块"""
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        return self.chunk_text(md_text, source_path=file_path)

    def chunk_text(self, markdown_text: str, source_path: str = "") -> list[Chunk]:
        """解析 Markdown 文本并分块"""
        doc = parse_markdown(markdown_text)
        return self.chunk_document(doc, source_path)

    def _build_sections(self, children: list) -> list[dict]:
        """按标题层级将子节点分组为 sections"""
        sections = []
        current_section = self._new_section()
        heading_stack = []  # [(level, text), ...]

        for child in children:
            if isinstance(child, HeadingNode) and self.config.respect_headings:
                if current_section["nodes"]:
                    sections.append(current_section)
                    current_section = self._new_section()

                # 维护标题栈
                while heading_stack and heading_stack[-1][0] >= child.level:
                    heading_stack.pop()
                heading_stack.append((child.level, child.raw_text))

                current_section["heading_stack"] = list(heading_stack)
                current_section["nodes"].append(child)
            else:
                current_section["nodes"].append(child)

        if current_section["nodes"]:
            sections.append(current_section)

        return sections

    def _new_section(self) -> dict:
        return {
            "heading_stack": [],
            "nodes": [],
        }

    def _get_heading_path(self, heading_stack: list) -> str:
        return " > ".join(h[1] for h in heading_stack) if heading_stack else ""

    def _split_section(self, section: dict) -> list[Chunk]:
        """将一个 section 拆分为一个或多个 Chunk"""
        heading_path = self._get_heading_path(section["heading_stack"])
        nodes = section["nodes"]

        if not nodes:
            return []

        chunk = self._build_chunk(nodes, heading_path)
        plain_text = chunk.text

        if len(plain_text) <= self.config.chunk_size:
            return [chunk]

        # 超长 section，在段落边界分割
        return self._split_oversized(nodes, heading_path)

    def _split_oversized(self, nodes: list, heading_path: str) -> list[Chunk]:
        """在段落边界分割过长的 section"""
        chunks = []
        current_nodes = []

        for node in nodes:
            current_nodes.append(node)
            current_len = sum(
                len(self._extract_plain_text(n)) for n in current_nodes
            )

            is_split_point = isinstance(node, (
                ParagraphNode, CodeBlockNode, TableNode,
                HorizontalRuleNode, BlockquoteNode,
            ))

            if is_split_point and current_len >= self.config.chunk_size:
                chunk = self._build_chunk(current_nodes, heading_path)
                if len(chunk.text) >= self.config.min_chunk_size:
                    chunks.append(chunk)
                # overlap: 保留最后一个节点作为 overlap
                if len(current_nodes) > 1 and self.config.chunk_overlap > 0:
                    current_nodes = [current_nodes[-1]]
                else:
                    current_nodes = []

        if current_nodes:
            chunk = self._build_chunk(current_nodes, heading_path)
            if len(chunk.text) >= self.config.min_chunk_size:
                chunks.append(chunk)

        return chunks

    def _build_chunk(self, nodes: list, heading_path: str) -> Chunk:
        """从节点列表构建单个 Chunk"""
        chunk_id = uuid.uuid4().hex[:12]
        plain_text = "\n".join(
            self._extract_plain_text(n) for n in nodes if self._extract_plain_text(n).strip()
        )
        md_text = self._nodes_to_markdown(nodes)

        metadata = {
            "heading_path": heading_path,
            "node_count": len(nodes),
            "char_count": len(plain_text),
        }
        if nodes and hasattr(nodes[0], "line"):
            metadata["start_line"] = nodes[0].line
        if nodes and hasattr(nodes[-1], "line"):
            metadata["end_line"] = nodes[-1].line

        return Chunk(id=chunk_id, text=plain_text, markdown=md_text, metadata=metadata)

    def _extract_plain_text(self, node) -> str:
        """递归提取纯文本（复用 analyzer._extract_text 类似逻辑）"""
        if isinstance(node, TextNode):
            return node.value
        elif isinstance(node, HeadingNode):
            return node.raw_text
        elif isinstance(node, ParagraphNode):
            return node.raw_text
        elif isinstance(node, CodeBlockNode):
            return node.code
        elif isinstance(node, ListItemNode):
            return self._inline_text(node.content)
        elif isinstance(node, TaskItemNode):
            prefix = "[x] " if node.checked else "[ ] "
            return prefix + self._inline_text(node.content)
        elif isinstance(node, (UnorderedListNode, OrderedListNode)):
            return "\n".join(
                self._extract_plain_text(item) for item in node.items
            )
        elif isinstance(node, TableNode):
            lines = [" | ".join(str(c) for c in node.headers)]
            for row in node.rows:
                lines.append(" | ".join(str(c) for c in row.cells))
            return "\n".join(lines)
        elif isinstance(node, BlockquoteNode):
            texts = []
            for c in node.content:
                text = self._extract_plain_text(c)
                if text:
                    texts.append(text)
            return "\n".join(texts)
        elif isinstance(node, HorizontalRuleNode):
            return "---"
        elif isinstance(node, DocumentNode):
            texts = []
            for c in node.children:
                text = self._extract_plain_text(c)
                if text:
                    texts.append(text)
            return "\n".join(texts)
        elif hasattr(node, "content") and isinstance(node.content, list):
            return self._inline_text(node.content)
        return str(node) if node else ""

    def _inline_text(self, nodes: list) -> str:
        """内联节点列表转纯文本"""
        parts = []
        for n in nodes:
            if isinstance(n, TextNode):
                parts.append(n.value)
            elif hasattr(n, "content") and isinstance(n.content, list):
                parts.append(self._inline_text(n.content))
            elif hasattr(n, "text"):
                parts.append(n.text)
            elif hasattr(n, "value"):
                parts.append(str(n.value))
        return "".join(parts)

    def _nodes_to_markdown(self, nodes: list) -> str:
        """节点列表转 Markdown 文本"""
        temp_doc = DocumentNode(children=nodes)
        return generate_markdown(temp_doc)
