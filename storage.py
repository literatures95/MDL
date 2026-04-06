"""MDL 存储引擎 - Markdown 文档的拆分、序列化、反序列化"""

import json
import os
from datetime import datetime
from ast_nodes import *
from md_parser import parse_markdown, split_document
from md_generator import generate_markdown


class StorageEngine:
    """文档存储引擎 - 支持多种格式的持久化操作"""

    def __init__(self):
        self._documents: dict[str, DocumentNode] = {}

    def load(self, path: str, alias: str = "doc", encoding: str = "utf-8") -> DocumentNode:
        """加载 Markdown 文件并解析为 AST"""
        with open(path, "r", encoding=encoding) as f:
            source = f.read()
        doc = parse_markdown(source)
        doc.metadata["source_path"] = os.path.abspath(path)
        doc.metadata["loaded_at"] = datetime.now().isoformat()
        doc.metadata["original_source"] = source
        self._documents[alias] = doc
        return doc

    def save(self, doc: DocumentNode, path: str, encoding: str = "utf-8"):
        """将 AST 保存为 Markdown 文件"""
        md_text = generate_markdown(doc)
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(md_text)
        doc.metadata["saved_at"] = datetime.now().isoformat()
        doc.metadata["save_path"] = os.path.abspath(path)

    def split_to_json(self, doc: DocumentNode) -> dict:
        """将文档拆分为 JSON 可序列化的结构化数据"""
        result = {
            "metadata": {
                "total_elements": len(doc.children),
                "created_at": datetime.now().isoformat(),
            },
            "structure": [],
            "elements": {
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
            },
        }
        for child in doc.children:
            elem = self._node_to_dict(child)
            type_key = self._get_type_key(child)
            if type_key in result["elements"]:
                result["elements"][type_key].append(elem)
            result["structure"].append({"type": child.node_type.name, "line": child.line})
        for child in doc.children:
            self._extract_inline_elements(child, result["elements"])
        return result

    def _node_to_dict(self, node) -> dict:
        """将 AST 节点转换为字典"""
        data = {"type": node.node_type.name, "line": getattr(node, "line", 0)}
        if isinstance(node, HeadingNode):
            data.update(level=node.level, text=node.raw_text, content=self._inline_to_text(node.content))
        elif isinstance(node, ParagraphNode):
            data.update(text=node.raw_text, content=self._inline_to_text(node.content))
        elif isinstance(node, CodeBlockNode):
            data.update(code=node.code, language=node.language, fenced=node.fenced)
        elif isinstance(node, BlockquoteNode):
            data.update(level=node.level, content=[self._node_to_dict(c) for c in (node.content or [])])
        elif isinstance(node, (UnorderedListNode, OrderedListNode)):
            data.update(marker=getattr(node, "marker", "-"), items=[self._list_item_to_dict(item) for item in node.items])
            if isinstance(node, OrderedListNode):
                data["start"] = node.start
        elif isinstance(node, TaskListNode):
            data.update(items=[self._task_item_to_dict(item) for item in node.items])
        elif isinstance(node, TableNode):
            data.update(headers=[c.content for c in node.headers], rows=[[c.content for c in row.cells] for row in node.rows], alignments=node.alignments)
        elif isinstance(node, HorizontalRuleNode):
            data.update(style=node.style)
        elif isinstance(node, HTMLBlockNode):
            data.update(html=node.html, tag=node.tag)
        return data

    def _list_item_to_dict(self, item) -> dict:
        """列表项转字典"""
        return {
            "content": self._inline_to_text(item.content),
            "checked": item.checked,
        }

    def _task_item_to_dict(self, item) -> dict:
        """任务项转字典"""
        return {
            "content": self._inline_to_text(item.content),
            "checked": item.checked,
        }

    def _inline_to_text(self, nodes) -> str:
        """行内节点列表转纯文本"""
        if nodes is None:
            return ""
        parts = []
        for node in nodes:
            if isinstance(node, TextNode):
                parts.append(node.value)
            elif isinstance(node, CodeInlineNode):
                parts.append(node.code)
            elif isinstance(node, (BoldNode, ItalicNode, BoldItalicNode, StrikethroughNode)):
                parts.append(self._inline_to_text(node.content))
            elif isinstance(node, LinkNode):
                parts.append(node.text)
            elif isinstance(node, ImageNode):
                parts.append(f"[图片: {node.alt}]")
            else:
                parts.append(str(getattr(node, "value", "")))
        return "".join(parts)

    def _extract_inline_elements(self, node, elements_dict: dict):
        """递归提取内联元素（链接和图片）"""
        if isinstance(node, LinkNode):
            elements_dict["links"].append({"text": node.text, "url": node.url, "title": node.title})
        elif isinstance(node, ImageNode):
            elements_dict["images"].append({"alt": node.alt, "src": node.src, "title": node.title})
        if hasattr(node, "content") and isinstance(node.content, list):
            for child in node.content:
                self._extract_inline_elements(child, elements_dict)

    def _get_type_key(self, node) -> str:
        """获取元素类型对应的键名"""
        mapping = {
            NodeType.HEADING: "headings",
            NodeType.PARAGRAPH: "paragraphs",
            NodeType.CODE_BLOCK: "code_blocks",
            NodeType.UNORDERED_LIST: "lists",
            NodeType.ORDERED_LIST: "lists",
            NodeType.TASK_LIST: "lists",
            NodeType.BLOCKQUOTE: "blockquotes",
            NodeType.TABLE: "tables",
            NodeType.HORIZONTAL_RULE: "horizontal_rules",
            NodeType.HTML_BLOCK: "html_blocks",
        }
        return mapping.get(node.node_type, "other")

    def export_json(self, doc: DocumentNode, path: str, pretty: bool = True):
        """导出文档为 JSON 文件"""
        data = self.split_to_json(doc)
        indent = 4 if pretty else None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

    def import_json(self, path: str) -> DocumentNode:
        """从 JSON 文件导入并重建 AST"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self._dict_to_document(data)

    def _dict_to_document(self, data: dict) -> DocumentNode:
        """从字典重建文档 AST"""
        doc = DocumentNode(metadata=data.get("metadata", {}))
        for elem_data in data.get("elements", {}).get("headings", []):
            doc.children.append(HeadingNode(
                level=elem_data.get("level", 1),
                raw_text=elem_data.get("text", ""),
                content=[TextNode(value=elem_data.get("text", ""))],
            ))
        for elem_data in data.get("elements", {}).get("paragraphs", []):
            doc.children.append(ParagraphNode(
                raw_text=elem_data.get("text", ""),
                content=[TextNode(value=elem_data.get("text", ""))],
            ))
        for elem_data in data.get("elements", {}).get("code_blocks", []):
            doc.children.append(CodeBlockNode(
                code=elem_data.get("code", ""),
                language=elem_data.get("language", ""),
                fenced=elem_data.get("fenced", True),
            ))
        for elem_data in data.get("elements", {}).get("blockquotes", []):
            inner_content = [TextNode(value=str(c)) for c in elem_data.get("content", [])]
            doc.children.append(BlockquoteNode(content=inner_content, level=elem_data.get("level", 1)))
        for elem_data in data.get("elements", {}).get("tables", []):
            headers = [TableCellNode(content=h) for h in elem_data.get("headers", [])]
            rows = []
            for row_cells in elem_data.get("rows", []):
                rows.append(TableRowNode(cells=[TableCellNode(content=c) for c in row_cells]))
            doc.children.append(TableNode(headers=headers, rows=rows, alignments=elem_data.get("alignments", [])))
        for elem_data in data.get("elements", {}).get("horizontal_rules", []):
            doc.children.append(HorizontalRuleNode(style=elem_data.get("style", "***")))
        return doc

    def split_by_sections(self, doc: DocumentNode) -> list[dict]:
        """按章节拆分文档（以标题为分界）"""
        sections = []
        current_section = None
        for child in doc.children:
            if isinstance(child, HeadingNode):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "heading": {"level": child.level, "text": child.raw_text},
                    "children": [],
                    "start_line": child.line,
                }
            if current_section is not None:
                current_section["children"].append(child)
            else:
                current_section = {
                    "heading": None,
                    "children": [child],
                    "start_line": getattr(child, "line", 0),
                }
                sections = []
        if current_section:
            sections.append(current_section)
        return sections

    def extract_section(self, doc: DocumentNode, heading_text: str) -> Optional[DocumentNode]:
        """提取指定标题下的章节内容"""
        target_section = None
        found = False
        for i, child in enumerate(doc.children):
            if isinstance(child, HeadingNode) and child.raw_text == heading_text:
                found = True
                target_section = DocumentNode(children=[], metadata={"section_title": heading_text})
                continue
            if found:
                if isinstance(child, HeadingNode) and child.level <= 1:
                    break
                target_section.children.append(child)
        return target_section

    def serialize_ast(self, doc: DocumentNode) -> str:
        """将完整 AST 序列化为 JSON 字符串"""
        return json.dumps(doc.to_dict(), ensure_ascii=False, indent=2)

    def deserialize_ast(self, json_str: str) -> DocumentNode:
        """从 JSON 字符串反序列化 AST（基础版本，仅恢复结构信息）"""
        data = json.loads(json_str)
        return self._dict_to_document(data)

    def get_document(self, alias: str = "doc") -> Optional[DocumentNode]:
        """获取已加载的文档"""
        return self._documents.get(alias)


storage = StorageEngine()


def load_file(path: str, alias: str = "doc") -> DocumentNode:
    """便捷函数：加载 Markdown 文件"""
    return storage.load(path, alias)


def save_file(doc: DocumentNode, path: str):
    """便捷函数：保存 Markdown 文件"""
    storage.save(doc, path)


def to_json(doc: DocumentNode) -> dict:
    """便捷函数：文档 → 结构化 JSON"""
    return storage.split_to_json(doc)


def from_json(data: dict | str) -> DocumentNode:
    """便捷函数：结构化 JSON → 文档"""
    if isinstance(data, str):
        return storage.import_json(data)
    return storage._dict_to_document(data)
