"""MDL 分析引擎 - Markdown 文档的深度统计分析"""

import re
from collections import Counter
from ast_nodes import (
    BoldItalicNode, BoldNode, CodeBlockNode, CodeInlineNode, DocumentNode,
    HeadingNode, ImageNode, ItalicNode, LinkNode, ListItemNode,
    OrderedListNode, ParagraphNode, StrikethroughNode, TableNode,
    TaskItemNode, TaskListNode, TextNode, UnorderedListNode,
)
from md_parser import parse_markdown


class DocumentAnalyzer:
    """文档分析器 - 提供全面的文档统计和分析功能"""

    def __init__(self, doc: DocumentNode = None):
        self.doc = doc

    def analyze(self, doc: DocumentNode = None) -> dict:
        """执行完整分析，返回所有统计数据"""
        if doc:
            self.doc = doc
        if not self.doc:
            return {}
        return {
            "overview": self.get_overview(),
            "structure": self.get_structure_analysis(),
            "headings": self.analyze_headings(),
            "content": self.analyze_content(),
            "links": self.analyze_links(),
            "images": self.analyze_images(),
            "code": self.analyze_code_blocks(),
            "lists": self.analyze_lists(),
            "tables": self.analyze_tables(),
            "readability": self.readability_score(),
            "health": self.health_check(),
        }

    def get_overview(self) -> dict:
        """获取文档概览"""
        if not self.doc:
            return {}
        total_chars = 0
        total_words = 0
        total_lines = 0
        for child in self.doc.children:
            text = self._extract_text(child)
            total_chars += len(text)
            total_words += len(text.split())
            total_lines += text.count("\n") + 1
        return {
            "total_elements": len(self.doc.children),
            "total_characters": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "element_types": self._count_element_types(),
        }

    def _count_element_types(self) -> dict[str, int]:
        """统计各类型元素数量"""
        counter = Counter()
        for child in self.doc.children:
            counter[child.node_type.name] += 1
        return dict(counter)

    def get_structure_analysis(self) -> list[dict]:
        """获取文档结构大纲"""
        structure = []
        for child in self.doc.children:
            info = {"type": child.node_type.name, "line": getattr(child, "line", 0)}
            if isinstance(child, HeadingNode):
                info["level"] = child.level
                info["text"] = child.raw_text
                info["word_count"] = len(child.raw_text.split())
            elif isinstance(child, ParagraphNode):
                info["char_count"] = len(child.raw_text)
                info["word_count"] = len(child.raw_text.split())
            elif isinstance(child, CodeBlockNode):
                info["language"] = child.language or "text"
                info["lines"] = len(child.code.split("\n"))
            elif isinstance(child, (UnorderedListNode, OrderedListNode)):
                info["item_count"] = len(child.items)
            elif isinstance(child, TableNode):
                info["rows"] = len(child.rows) if hasattr(child, 'rows') else 0
                info["cols"] = len(child.headers) if hasattr(child, 'headers') else 0
            structure.append(info)
        return structure

    def analyze_headings(self) -> dict:
        """分析标题结构"""
        headings = [c for c in self.doc.children if isinstance(c, HeadingNode)]
        levels = [h.level for h in headings]
        level_counts = Counter(levels)
        hierarchy_ok = True
        prev_level = 0
        for level in levels:
            if level > prev_level + 1 and prev_level > 0:
                hierarchy_ok = False
            prev_level = level
        return {
            "count": len(headings),
            "by_level": {f"H{k}": v for k, v in sorted(level_counts.items())},
            "hierarchy_valid": hierarchy_ok,
            "titles": [{"level": h.level, "text": h.raw_text} for h in headings],
            "max_depth": max(levels) if levels else 0,
            "toc": self._generate_toc(headings),
        }

    def _generate_toc(self, headings: list) -> str:
        """生成目录文本"""
        lines = []
        for h in headings:
            indent = "  " * (h.level - 1)
            lines.append(f"{indent}- {h.raw_text}")
        return "\n".join(lines)

    def analyze_content(self) -> dict:
        """分析内容特征"""
        paragraphs = [c for c in self.doc.children if isinstance(c, ParagraphNode)]
        all_text = " ".join(p.raw_text for p in paragraphs)
        words = all_text.split()
        sentences = re.split(r"[.!?。！？]+", all_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", all_text))
        english_words = len(re.findall(r"[a-zA-Z]+", all_text))
        numbers = len(re.findall(r"\d+", all_text))
        return {
            "paragraph_count": len(paragraphs),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "chinese_char_count": chinese_chars,
            "english_word_count": english_words,
            "number_count": numbers,
            "unique_words": len(set(w.lower() for w in words)),
            "vocabulary_richness": round(len(set(w.lower() for w in words)) / len(words), 4) if words else 0,
        }

    def analyze_links(self) -> dict:
        """分析链接"""
        links = []
        self._collect_links(self.doc.children, links)
        url_domains = Counter()
        broken_schemes = []
        for link in links:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(link.url)
                if parsed.netloc:
                    url_domains[parsed.netloc] += 1
                elif link.url and not link.url.startswith(("#", "/", "http", "mailto", "tel")):
                    broken_schemes.append(link.url)
            except Exception:
                pass
        return {
            "total_links": len(links),
            "internal_links": [link for link in links if link.url.startswith("#")],
            "external_links": [link for link in links if not link.url.startswith("#")],
            "domains": dict(url_domains.most_common(10)),
            "potentially_broken": broken_schemes,
            "detail": [{"text": link.text, "url": link.url} for link in links[:20]],
        }

    def _collect_links(self, nodes, result: list):
        """递归收集链接"""
        for node in nodes:
            if isinstance(node, LinkNode):
                result.append(node)
            if hasattr(node, "content") and isinstance(node.content, list):
                self._collect_links(node.content, result)

    def analyze_images(self) -> dict:
        """分析图片"""
        images = []
        self._collect_images(self.doc.children, images)
        formats = Counter()
        for img in images:
            src_lower = img.src.lower()
            if src_lower.endswith(".png"):
                formats["PNG"] += 1
            elif src_lower.endswith((".jpg", ".jpeg")):
                formats["JPEG"] += 1
            elif src_lower.endswith(".gif"):
                formats["GIF"] += 1
            elif src_lower.endswith(".svg"):
                formats["SVG"] += 1
            elif src_lower.endswith(".webp"):
                formats["WebP"] += 1
            else:
                formats["其他"] += 1
        return {
            "total_images": len(images),
            "formats": dict(formats),
            "with_alt_text": sum(1 for img in images if img.alt),
            "without_alt_text": sum(1 for img in images if not img.alt),
            "detail": [{"alt": img.alt, "src": img.src} for img in images],
        }

    def _collect_images(self, nodes, result: list):
        """递归收集图片"""
        for node in nodes:
            if isinstance(node, ImageNode):
                result.append(node)
            if hasattr(node, "content") and isinstance(node.content, list):
                self._collect_images(node.content, result)

    def analyze_code_blocks(self) -> dict:
        """分析代码块"""
        code_blocks = [c for c in self.doc.children if isinstance(c, CodeBlockNode)]
        languages = Counter(cb.language or "unknown" for cb in code_blocks)
        total_lines = sum(len(cb.code.split("\n")) for cb in code_blocks)
        total_chars = sum(len(cb.code) for cb in code_blocks)
        return {
            "count": len(code_blocks),
            "languages": dict(languages),
            "total_lines": total_lines,
            "total_characters": total_chars,
            "avg_block_size": round(total_lines / len(code_blocks), 1) if code_blocks else 0,
            "fenced_count": sum(1 for cb in code_blocks if cb.fenced),
            "indented_count": sum(1 for cb in code_blocks if not cb.fenced),
            "detail": [
                {"language": cb.language or "text", "lines": len(cb.code.split("\n")), "chars": len(cb.code)}
                for cb in code_blocks
            ],
        }

    def analyze_lists(self) -> dict:
        """分析列表"""
        lists = [c for c in self.doc.children if isinstance(c, (UnorderedListNode, OrderedListNode, TaskListNode))]
        total_items = 0
        task_completed = 0
        task_total = 0
        for lst in lists:
            total_items += len(lst.items)
            if isinstance(lst, TaskListNode):
                for item in lst.items:
                    task_total += 1
                    if item.checked:
                        task_completed += 1
        return {
            "list_count": len(lists),
            "total_items": total_items,
            "unordered": sum(1 for lst in lists if isinstance(lst, UnorderedListNode)),
            "ordered": sum(1 for lst in lists if isinstance(lst, OrderedListNode)),
            "task_lists": sum(1 for lst in lists if isinstance(lst, TaskListNode)),
            "task_completion": round(task_completed / task_total * 100, 1) if task_total else 0,
            "task_done": task_completed,
            "task_total": task_total,
        }

    def analyze_tables(self) -> dict:
        """分析表格"""
        tables = [c for c in self.doc.children if isinstance(c, TableNode)]
        total_cells = 0
        for table in tables:
            total_cells += len(table.headers)
            for row in table.rows:
                total_cells += len(row.cells)
        return {
            "count": len(tables),
            "total_cells": total_cells,
            "avg_rows": round(sum(len(t.rows) for t in tables) / len(tables), 1) if tables else 0,
            "avg_cols": round(sum(len(t.headers) for t in tables) / len(tables), 1) if tables else 0,
            "detail": [
                {"headers": len(t.headers), "rows": len(t.rows)} for t in tables
            ],
        }

    def readability_score(self) -> dict:
        """可读性评分"""
        content_info = self.analyze_content()
        words = content_info.get("word_count", 0)
        sentences = content_info.get("sentence_count", 0)
        if words == 0 or sentences == 0:
            return {"score": 0, "level": "无法评估", "method": "无内容"}
        syllable_estimate = sum(self._estimate_syllables(w) for w in self._get_all_words())
        if syllable_estimate == 0:
            syllable_estimate = words * 1.5
        try:
            fk_grade = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllable_estimate / words)
            fk_grade = max(0, min(100, fk_grade))
            if fk_grade >= 90:
                level = "非常容易（5年级以下）"
            elif fk_grade >= 80:
                level = "容易（6年级）"
            elif fk_grade >= 70:
                level = "较易（7年级）"
            elif fk_grade >= 60:
                level = "中等（8-9年级）"
            elif fk_grade >= 50:
                level = "较难（10-12年级）"
            elif fk_grade >= 30:
                level = "困难（大学）"
            else:
                level = "非常困难（专家级）"
        except Exception:
            fk_grade = 0
            level = "计算异常"
        return {
            "score": round(fk_grade, 1),
            "level": level,
            "method": "Flesch-Kincaid 可读性指数",
            "words_per_sentence": round(words / sentences, 1),
            "syllables_per_word": round(syllable_estimate / words, 2) if words else 0,
        }

    def _get_all_words(self) -> list[str]:
        """获取所有单词"""
        words = []
        for child in self.doc.children:
            text = self._extract_text(child)
            words.extend(re.findall(r"[a-zA-Z]+", text))
        return words

    def _estimate_syllables(self, word: str) -> int:
        """估算英文音节数"""
        word = word.lower()
        if len(word) <= 2:
            return 1
        word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
        word = re.sub(r"^y", "", word)
        count = max(1, len(re.findall(r"[aeiouy]", word)))
        return count

    def health_check(self) -> dict:
        """文档健康检查"""
        issues = []
        warnings = []
        headings = [c for c in self.doc.children if isinstance(c, HeadingNode)]
        heading_texts = [h.raw_text.lower() for h in headings]
        if len(set(heading_texts)) != len(heading_texts):
            issues.append("存在重复标题")
        if headings and headings[0].level != 1:
            warnings.append("首标题不是 H1")
        images = []
        self._collect_images(self.doc.children, images)
        missing_alt = [img for img in images if not img.alt]
        if missing_alt:
            warnings.append(f"{len(missing_alt)} 张图片缺少 alt 文本")
        links = []
        self._collect_links(self.doc.children, links)
        empty_link_text = [link for link in links if not link.text.strip()]
        if empty_link_text:
            warnings.append(f"{len(empty_link_text)} 个链接缺少描述文本")
        long_paragraphs = [p for p in self.doc.children if isinstance(p, ParagraphNode) and len(p.raw_text) > 500]
        if long_paragraphs:
            warnings.append(f"{len(long_paragraphs)} 个段落超过 500 字符，建议拆分")
        code_blocks = [c for c in self.doc.children if isinstance(c, CodeBlockNode) and not c.language]
        if code_blocks:
            warnings.append(f"{len(code_blocks)} 个代码块未指定语言，影响语法高亮")
        score = 100 - len(issues) * 15 - len(warnings) * 5
        score = max(0, min(100, score))
        return {
            "score": score,
            "issues": issues,
            "warnings": warnings,
            "status": "健康" if score >= 80 else ("良好" if score >= 60 else ("需改进" if score >= 30 else "不健康")),
        }

    def find_text(self, query: str, case_sensitive: bool = False) -> list[dict]:
        """在文档中搜索文本"""
        results = []
        search_query = query if case_sensitive else query.lower()
        for i, child in enumerate(self.doc.children):
            text = self._extract_text(child)
            check_text = text if case_sensitive else text.lower()
            if search_query in check_text:
                positions = []
                start = 0
                while True:
                    pos = check_text.find(search_query, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                results.append({
                    "index": i,
                    "type": child.node_type.name,
                    "line": getattr(child, "line", 0),
                    "context": text[max(0, positions[0] - 30):positions[0] + len(query) + 30],
                    "match_count": len(positions),
                })
        return results

    def compare_documents(self, other_doc: DocumentNode) -> dict:
        """比较两个文档的差异"""
        my_elements = [(c.node_type.name, self._extract_text(c)[:100]) for c in self.doc.children]
        other_elements = [(c.node_type.name, self._extract_text(c)[:100]) for c in other_doc.children]
        only_in_self = [e for e in my_elements if e not in other_elements]
        only_in_other = [e for e in other_elements if e not in my_elements]
        common = [e for e in my_elements if e in other_elements]
        return {
            "self_elements": len(my_elements),
            "other_elements": len(other_elements),
            "common": len(common),
            "only_in_first": only_in_self,
            "only_in_second": only_in_other,
            "similarity": round(len(common) / max(len(my_elements), len(other_elements), 1) * 100, 1),
        }

    def _extract_text(self, node) -> str:
        """从节点提取纯文本"""
        if isinstance(node, TextNode):
            return node.value
        if isinstance(node, ParagraphNode):
            return node.raw_text or ""
        if isinstance(node, HeadingNode):
            return node.raw_text or ""
        if isinstance(node, CodeBlockNode):
            return node.code
        if isinstance(node, CodeInlineNode):
            return node.code
        if isinstance(node, (BoldNode, ItalicNode, BoldItalicNode, StrikethroughNode)):
            return "".join(self._extract_text(c) for c in (node.content or []))
        if isinstance(node, ListItemNode) or isinstance(node, TaskItemNode):
            return "".join(self._extract_text(c) for c in (node.content or []))
        if isinstance(node, LinkNode):
            return node.text
        if isinstance(node, ImageNode):
            return node.alt
        return ""


def analyze(doc: DocumentNode) -> dict:
    """便捷函数：对文档进行完整分析"""
    analyzer = DocumentAnalyzer(doc)
    return analyzer.analyze()


def quick_stats(source: str) -> dict:
    """便捷函数：快速统计 Markdown 源文本"""
    doc = parse_markdown(source)
    analyzer = DocumentAnalyzer(doc)
    return analyzer.get_overview()
