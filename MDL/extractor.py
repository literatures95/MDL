"""MDL 结构化提取模块 - 从文档中提取结构化数据"""

import re
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ExtractionSchema:
    """提取模式定义"""
    name: str
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_json_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "object",
            "properties": {
                name: {
                    "type": field_def.get("type", "string"),
                    "description": field_def.get("description", ""),
                    **{k: v for k, v in field_def.items() if k not in ("type", "description", "extractor")}
                }
                for name, field_def in self.fields.items()
            },
            "required": [name for name, f in self.fields.items() if f.get("required", False)],
        }


class StructuredExtractor:
    """结构化数据提取器"""

    def __init__(self):
        self.extractors: Dict[str, Callable] = {
            "title": self._extract_title,
            "headings": self._extract_headings,
            "paragraphs": self._extract_paragraphs,
            "links": self._extract_links,
            "images": self._extract_images,
            "tables": self._extract_tables,
            "code_blocks": self._extract_code_blocks,
            "lists": self._extract_lists,
            "metadata": self._extract_metadata,
            "keywords": self._extract_keywords,
            "emails": self._extract_emails,
            "urls": self._extract_urls,
            "dates": self._extract_dates,
            "numbers": self._extract_numbers,
        }

    def extract(self, markdown: str, schema: ExtractionSchema) -> Dict[str, Any]:
        """根据模式提取数据"""
        result = {}
        for field_name, field_def in schema.fields.items():
            extractor_name = field_def.get("extractor", field_name)
            if extractor_name in self.extractors:
                value = self.extractors[extractor_name](markdown, field_def)
                result[field_name] = value
        return result

    def _extract_title(self, markdown: str, config: Dict = None) -> Optional[str]:
        """提取标题"""
        match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_headings(self, markdown: str, config: Dict = None) -> List[Dict[str, Any]]:
        """提取所有标题"""
        headings = []
        for match in re.finditer(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({"level": level, "text": text})
        return headings

    def _extract_paragraphs(self, markdown: str, config: Dict = None) -> List[str]:
        """提取段落"""
        blocks = re.split(r"\n{2,}", markdown)
        paragraphs = []
        for block in blocks:
            block = block.strip()
            if block and not block.startswith(("#", "-", "*", ">", "|", "`", "```")):
                clean = re.sub(r"[#*`\[\]]", "", block)
                if clean.strip():
                    paragraphs.append(clean.strip())
        return paragraphs

    def _extract_links(self, markdown: str, config: Dict = None) -> List[Dict[str, str]]:
        """提取链接"""
        links = []
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", markdown):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
            })
        return links

    def _extract_images(self, markdown: str, config: Dict = None) -> List[Dict[str, str]]:
        """提取图片"""
        images = []
        for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", markdown):
            images.append({
                "alt": match.group(1),
                "src": match.group(2),
            })
        return images

    def _extract_tables(self, markdown: str, config: Dict = None) -> List[Dict[str, Any]]:
        """提取表格"""
        tables = []
        table_pattern = r"(\|[^\n]+\|\n)+(\|[-:| ]+\|\n)?(\|[^\n]+\|\n?)*"
        for match in re.finditer(table_pattern, markdown):
            table_text = match.group(0)
            lines = [l for l in table_text.strip().split("\n") if l.strip()]
            if len(lines) < 2:
                continue
            headers = [c.strip() for c in lines[0].split("|") if c.strip()]
            rows = []
            for line in lines[2:]:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if cells:
                    rows.append(cells)
            tables.append({"headers": headers, "rows": rows})
        return tables

    def _extract_code_blocks(self, markdown: str, config: Dict = None) -> List[Dict[str, str]]:
        """提取代码块"""
        blocks = []
        pattern = r"```(\w*)\n(.*?)```"
        for match in re.finditer(pattern, markdown, re.DOTALL):
            blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2).strip(),
            })
        return blocks

    def _extract_lists(self, markdown: str, config: Dict = None) -> List[Dict[str, Any]]:
        """提取列表"""
        lists = []
        current_list = {"type": None, "items": []}
        for line in markdown.split("\n"):
            ul_match = re.match(r"^[-*+]\s+(.+)$", line)
            ol_match = re.match(r"^\d+\.\s+(.+)$", line)
            if ul_match:
                if current_list["type"] != "unordered" and current_list["items"]:
                    lists.append(current_list)
                    current_list = {"type": None, "items": []}
                current_list["type"] = "unordered"
                current_list["items"].append(ul_match.group(1))
            elif ol_match:
                if current_list["type"] != "ordered" and current_list["items"]:
                    lists.append(current_list)
                    current_list = {"type": None, "items": []}
                current_list["type"] = "ordered"
                current_list["items"].append(ol_match.group(1))
        if current_list["items"]:
            lists.append(current_list)
        return lists

    def _extract_metadata(self, markdown: str, config: Dict = None) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {}
        frontmatter_match = re.match(r"^---\n(.*?)\n---", markdown, re.DOTALL)
        if frontmatter_match:
            for line in frontmatter_match.group(1).split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
        return metadata

    def _extract_keywords(self, markdown: str, config: Dict = None) -> List[str]:
        """提取关键词"""
        text = re.sub(r"[#*`\[\]()>|-]", " ", markdown)
        text = re.sub(r"\s+", " ", text)
        words = [w.lower() for w in text.split() if len(w) > 3]
        word_freq: Dict[str, int] = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_n = config.get("top_n", 10) if config else 10
        return [w for w, _ in sorted_words[:top_n]]

    def _extract_emails(self, markdown: str, config: Dict = None) -> List[str]:
        """提取邮箱地址"""
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        return list(set(re.findall(pattern, markdown)))

    def _extract_urls(self, markdown: str, config: Dict = None) -> List[str]:
        """提取 URL"""
        pattern = r"https?://[^\s<>\[\]()\"']+"
        urls = re.findall(pattern, markdown)
        link_urls = [u for _, u in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown)]
        return list(set(urls + link_urls))

    def _extract_dates(self, markdown: str, config: Dict = None) -> List[str]:
        """提取日期"""
        patterns = [
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
            r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",
            r"\d{4}年\d{1,2}月\d{1,2}日",
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, markdown))
        return list(set(dates))

    def _extract_numbers(self, markdown: str, config: Dict = None) -> List[float]:
        """提取数字"""
        pattern = r"-?\d+\.?\d*"
        numbers = []
        for match in re.finditer(pattern, markdown):
            try:
                num = float(match.group())
                numbers.append(num)
            except ValueError:
                continue
        return numbers


DEFAULT_SCHEMAS: Dict[str, ExtractionSchema] = {
    "basic": ExtractionSchema(
        name="basic",
        fields={
            "title": {"type": "string", "description": "文档标题"},
            "headings": {"type": "array", "description": "所有标题"},
            "links": {"type": "array", "description": "所有链接"},
        },
    ),
    "full": ExtractionSchema(
        name="full",
        fields={
            "title": {"type": "string"},
            "headings": {"type": "array"},
            "paragraphs": {"type": "array"},
            "links": {"type": "array"},
            "images": {"type": "array"},
            "tables": {"type": "array"},
            "code_blocks": {"type": "array"},
            "keywords": {"type": "array", "top_n": 20},
        },
    ),
    "contact": ExtractionSchema(
        name="contact",
        fields={
            "emails": {"type": "array", "description": "邮箱地址"},
            "urls": {"type": "array", "description": "网址"},
        },
    ),
}


def extract_structured(markdown: str, schema_name: str = "basic") -> Dict[str, Any]:
    """结构化提取的便捷函数"""
    extractor = StructuredExtractor()
    schema = DEFAULT_SCHEMAS.get(schema_name, DEFAULT_SCHEMAS["basic"])
    return extractor.extract(markdown, schema)


def extract_with_custom_schema(markdown: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """使用自定义模式提取"""
    extraction_schema = ExtractionSchema(
        name=schema.get("name", "custom"),
        fields=schema.get("fields", {}),
    )
    extractor = StructuredExtractor()
    return extractor.extract(markdown, extraction_schema)
