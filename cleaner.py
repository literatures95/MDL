"""MDL 文档清理模块 - 移除页眉、页脚、伪影等"""

import re
from typing import List, Set
from dataclasses import dataclass


@dataclass
class CleanerConfig:
    """清理器配置"""
    remove_headers: bool = True
    remove_footers: bool = True
    remove_page_numbers: bool = True
    remove_empty_lines: bool = True
    remove_repeated_text: bool = True
    min_repeat_count: int = 3
    header_patterns: List[str] = None
    footer_patterns: List[str] = None

    def __post_init__(self):
        if self.header_patterns is None:
            self.header_patterns = [
                r"^第\s*\d+\s*页",
                r"^Page\s*\d+",
                r"^-\s*\d+\s*-$",
                r"^\d+\s*/\s*\d+$",
            ]
        if self.footer_patterns is None:
            self.footer_patterns = [
                r"^\d+$",
                r"^第\s*\d+\s*页",
                r"^Page\s*\d+",
                r"^-\s*\d+\s*-$",
                r"^\d+\s*/\s*\d+$",
                r"^\[?\d+\]?$",
            ]


class DocumentCleaner:
    """文档清理器"""

    def __init__(self, config: CleanerConfig = None):
        self.config = config or CleanerConfig()

    def clean(self, markdown: str) -> str:
        """清理 Markdown 文档"""
        lines = markdown.split("\n")
        lines = self._remove_page_numbers(lines)
        lines = self._remove_headers_footers(lines)
        lines = self._remove_repeated_text(lines)
        lines = self._remove_empty_lines(lines)
        return "\n".join(lines)

    def _remove_page_numbers(self, lines: List[str]) -> List[str]:
        """移除页码"""
        if not self.config.remove_page_numbers:
            return lines
        result = []
        for line in lines:
            is_page_num = False
            for pattern in self.config.footer_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_page_num = True
                    break
            if not is_page_num:
                result.append(line)
        return result

    def _remove_headers_footers(self, lines: List[str]) -> List[str]:
        """移除页眉页脚"""
        result = []
        for line in lines:
            stripped = line.strip()
            is_header_footer = False
            if self.config.remove_headers:
                for pattern in self.config.header_patterns:
                    if re.match(pattern, stripped, re.IGNORECASE):
                        is_header_footer = True
                        break
            if self.config.remove_footers and not is_header_footer:
                for pattern in self.config.footer_patterns:
                    if re.match(pattern, stripped, re.IGNORECASE):
                        is_header_footer = True
                        break
            if not is_header_footer:
                result.append(line)
        return result

    def _remove_repeated_text(self, lines: List[str]) -> List[str]:
        """移除重复文本"""
        if not self.config.remove_repeated_text:
            return lines
        line_counts: dict = {}
        for line in lines:
            stripped = line.strip()
            if stripped:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        repeated_lines: Set[str] = {
            line for line, count in line_counts.items()
            if count >= self.config.min_repeat_count and len(line) < 100
        }
        result = []
        for line in lines:
            if line.strip() not in repeated_lines:
                result.append(line)
        return result

    def _remove_empty_lines(self, lines: List[str]) -> List[str]:
        """移除多余空行"""
        if not self.config.remove_empty_lines:
            return lines
        result = []
        prev_empty = False
        for line in lines:
            is_empty = not line.strip()
            if is_empty:
                if not prev_empty:
                    result.append(line)
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        while result and not result[-1].strip():
            result.pop()
        while result and not result[0].strip():
            result.pop(0)
        return result


class ArtifactRemover:
    """伪影移除器"""

    @staticmethod
    def remove_unicode_artifacts(text: str) -> str:
        """移除 Unicode 伪影"""
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        text = re.sub(r"\ufffd", "", text)
        return text

    @staticmethod
    def fix_encoding_issues(text: str) -> str:
        """修复编码问题"""
        replacements = {
            "\u00e2\u20ac\u0153": '"',
            "\u00e2\u20ac": '"',
            "\u00e2\u20ac\u02dc": "'",
            "\u00e2\u20ac\u2122": "'",
            "\u00e2\u20ac\u009d": '"',
            "\u00e2\u20ac\u009c": '"',
            "\u00e2\u20ac\u201c": "-",
            "\u00e2\u20ac\u201d": "-",
            "\u00e2\u20ac\u00a6": "...",
            "\u00c3\u00a9": "e",
            "\u00c3\u00a8": "e",
            "\u00c3\u00aa": "e",
            "\u00c3\u00ab": "e",
            "\u00c3\u00a1": "a",
            "\u00c3\u00a0": "a",
            "\u00c3\u00a3": "a",
            "\u00c3\u00a7": "c",
            "\u00c3\u00b1": "n",
            "\u00c3\u00b6": "o",
            "\u00c3\u00bc": "u",
            "\u00c3\u0178": "ss",
        }
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """规范化空白字符"""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


class TableCleaner:
    """表格清理器"""

    @staticmethod
    def fix_table_formatting(markdown: str) -> str:
        """修复表格格式"""
        def fix_table(match):
            table = match.group(0)
            lines = table.strip().split("\n")
            if len(lines) < 2:
                return table
            header = lines[0]
            body = lines[2:] if len(lines) > 2 else []
            cols = len([c for c in header.split("|") if c.strip()])
            fixed_separator = "|" + "|".join(["---"] * cols) + "|"
            result = [header, fixed_separator] + body
            return "\n".join(result)
        table_pattern = r"(\|[^\n]+\|\n)+(\|[-:| ]+\|\n)?(\|[^\n]+\|\n?)*"
        return re.sub(table_pattern, fix_table, markdown, flags=re.MULTILINE)

    @staticmethod
    def merge_split_tables(markdown: str) -> str:
        """合并分割的表格"""
        lines = markdown.split("\n")
        result = []
        in_table = False
        current_table = []
        for line in lines:
            is_table_line = line.strip().startswith("|") and line.strip().endswith("|")
            if is_table_line:
                in_table = True
                current_table.append(line)
            else:
                if in_table:
                    if current_table:
                        result.extend(current_table)
                        result.append("")
                    current_table = []
                    in_table = False
                result.append(line)
        if current_table:
            result.extend(current_table)
        return "\n".join(result)


class LinkCleaner:
    """链接清理器"""

    @staticmethod
    def fix_broken_links(markdown: str) -> str:
        """修复损坏的链接"""
        markdown = re.sub(r"\[([^\]]*)\]\(\s*\)", r"\1", markdown)
        markdown = re.sub(r"\[\s*\]\(([^)]*)\)", r"\1", markdown)
        markdown = re.sub(r"\[([^\]]*)\]\(([^)]*)\s+\)", r"[\1](\2)", markdown)
        return markdown

    @staticmethod
    def normalize_urls(markdown: str) -> str:
        """规范化 URL"""
        def fix_url(match):
            text = match.group(1)
            url = match.group(2)
            url = re.sub(r"\s+", "", url)
            if not url.startswith(("http://", "https://", "mailto:", "#", "/")):
                url = "https://" + url
            return f"[{text}]({url})"
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", fix_url, markdown)


def clean_document(markdown: str, config: CleanerConfig = None) -> str:
    """清理文档的便捷函数"""
    cleaner = DocumentCleaner(config)
    result = cleaner.clean(markdown)
    result = ArtifactRemover.remove_unicode_artifacts(result)
    result = ArtifactRemover.fix_encoding_issues(result)
    result = ArtifactRemover.normalize_whitespace(result)
    result = TableCleaner.fix_table_formatting(result)
    result = LinkCleaner.fix_broken_links(result)
    return result
