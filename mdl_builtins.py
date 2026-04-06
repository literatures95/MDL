"""MDL 内置函数库 - 提供所有 Markdown 操作的内置函数"""

from ast_nodes import *
from md_parser import parse_markdown
from md_generator import generate_markdown, generate_inline, generate_node
from storage import StorageEngine, storage as _storage
from analyzer import DocumentAnalyzer
from converter import HTMLConverter, TextConverter


class Environment:
    """运行时环境 - 存储变量和文档"""

    def __init__(self):
        self.variables: dict = {}
        self.documents: dict[str, DocumentNode] = {}
        self.functions: dict = {}
        self.storage = StorageEngine()

    def get_doc(self, name: str = "doc") -> DocumentNode:
        return self.documents.get(name)

    def set_doc(self, name: str, doc: DocumentNode):
        self.documents[name] = doc

    def get_var(self, name: str):
        return self.variables.get(name)

    def set_var(self, name: str, value):
        self.variables[name] = value

    def has_var(self, name: str) -> bool:
        return name in self.variables

    def define_function(self, name: str, params: list, body: list):
        self.functions[name] = {"params": params, "body": body}


class BuiltinFunctions:
    """所有内置函数"""

    @staticmethod
    def load(env: Environment, path: str, alias: str = "doc") -> DocumentNode:
        """加载 Markdown 文件"""
        doc = env.storage.load(path, alias)
        env.set_doc(alias, doc)
        print(f"[MDL] 已加载文件: {path} (别名: {alias})")
        print(f"[MDL] 包含 {len(doc.children)} 个元素")
        return doc

    @staticmethod
    def save(env: Environment, target: str = "doc", path: str = ""):
        """保存文档为 Markdown 文件"""
        doc = env.get_doc(target)
        if not doc:
            raise RuntimeError(f"文档 '{target}' 不存在")
        save_path = path or f"{target}_output.md"
        env.storage.save(doc, save_path)
        print(f"[MDL] 已保存到: {save_path}")

    @staticmethod
    def print_value(value):
        """打印值"""
        if isinstance(value, DocumentNode):
            md_text = generate_markdown(value)
            print(md_text)
            return md_text
        elif isinstance(value, (HeadingNode, ParagraphNode, CodeBlockNode)):
            print(generate_node(value))
            return value
        elif isinstance(value, list):
            for item in value:
                BuiltinFunctions.print_value(item)
        elif isinstance(value, dict):
            import json
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(value)
        return value

    @staticmethod
    def set_property(env: Environment, target, property_name: str, value):
        """设置属性"""
        if isinstance(target, HeadingNode):
            if property_name in ("text", "raw_text"):
                target.raw_text = str(value) if not isinstance(value, str) else value
            elif property_name == "level":
                target.level = int(value)
        elif isinstance(target, ParagraphNode):
            if property_name in ("text", "raw_text"):
                target.raw_text = str(value) if not isinstance(value, str) else value
        elif isinstance(target, CodeBlockNode):
            if property_name == "code":
                target.code = str(value) if not isinstance(value, str) else value
            elif property_name == "language":
                target.language = str(value)
        elif isinstance(target, ListItemNode):
            if property_name == "checked":
                target.checked = bool(value)
        elif isinstance(target, TaskItemNode):
            if property_name == "checked":
                target.checked = bool(value)

    @staticmethod
    def insert_element(env: Environment, doc: DocumentNode, position: str, index: int, element):
        """在指定位置插入元素"""
        if position == "after":
            doc.children.insert(index + 1, element)
        elif position == "before":
            doc.children.insert(index, element)

    @staticmethod
    def append_element(env: Environment, doc: DocumentNode, element):
        """追加元素到文档末尾"""
        doc.children.append(element)

    @staticmethod
    def remove_element(env: Environment, doc: DocumentNode, index: int):
        """删除指定位置的元素"""
        if 0 <= index < len(doc.children):
            removed = doc.children.pop(index)
            print(f"[MDL] 已删除元素 (类型: {removed.node_type.name})")
            return removed
        raise IndexError(f"索引 {index} 超出范围")

    @staticmethod
    def convert_format(env: Environment, source, fmt: str, output_path: str = ""):
        """格式转换"""
        if fmt == "html":
            converter = HTMLConverter()
            result = converter.convert(source)
        elif fmt == "text":
            converter = TextConverter()
            result = converter.convert(source)
        elif fmt == "json":
            import json
            result = json.dumps(source.to_dict(), ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {fmt}")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"[MDL] 已转换为 {fmt.upper()} 并保存到: {output_path}")
        else:
            print(result)
        return result

    @staticmethod
    def load_url(env: Environment, url: str, alias: str = "url_doc") -> DocumentNode:
        """从网页加载并转换为 Markdown 文档"""
        try:
            from formats import URLHandler, convert_to_markdown
            
            # 从 URL 获取内容并转换为 Markdown
            markdown_content = convert_to_markdown(url)
            
            # 解析为 DocumentNode
            doc = parse_markdown(markdown_content)
            env.set_doc(alias, doc)
            
            print(f"[MDL] 已从 URL 加载内容: {url} (别名: {alias})")
            print(f"[MDL] 包含 {len(doc.children)} 个元素")
            return doc
        except ImportError:
            print("[MDL] 错误: 需要安装 requests 和 beautifulsoup4")
            print("[MDL] 执行: pip install requests beautifulsoup4")
            raise
        except Exception as e:
            print(f"[MDL] 错误: 无法加载 URL - {str(e)}")
            raise

    @staticmethod
    def extract_links(content) -> list:
        """从 Markdown 或 HTML 内容中提取所有链接"""
        import re

        links = []
        seen = set()

        md_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        html_pattern = re.compile(r'<a\s+href=(?:"|\')([^"\']+)(?:"|\')[^>]*>([^<]*)</a>', re.IGNORECASE)
        ref_pattern = re.compile(r'\[([^\]]+)\]:\s*([^\s]+)')
        bare_pattern = re.compile(r'(https?://[^\s\)\]]+)')

        for text, url in md_pattern.findall(content):
            if url not in seen:
                seen.add(url)
                links.append({"text": text, "url": url, "type": "markdown"})

        for url, text in html_pattern.findall(content):
            if url not in seen:
                seen.add(url)
                links.append({"text": text or url, "url": url, "type": "html"})

        for text, url in ref_pattern.findall(content):
            if url not in seen:
                seen.add(url)
                links.append({"text": text, "url": url, "type": "reference"})

        for url in bare_pattern.findall(content):
            if url not in seen:
                seen.add(url)
                links.append({"text": url, "url": url, "type": "bare"})

        return links

    @staticmethod
    def select_elements(doc: DocumentNode, element_type: str, index=None) -> list:
        """选择器 - 按类型选取元素"""
        type_map = {
            "h1": HeadingNode, "h2": HeadingNode, "h3": HeadingNode,
            "h4": HeadingNode, "h5": HeadingNode, "h6": HeadingNode,
            "heading": HeadingNode,
            "paragraph": ParagraphNode, "p": ParagraphNode,
            "codeblock": CodeBlockNode, "code": CodeBlockNode,
            "blockquote": BlockquoteNode, "quote": BlockquoteNode,
            "ul": UnorderedListNode, "ol": OrderedListNode,
            "list": (UnorderedListNode, OrderedListNode),
            "table": TableNode,
            "hr": HorizontalRuleNode, "rule": HorizontalRuleNode,
        }
        target_type = type_map.get(element_type.lower())
        if target_type is None:
            return []
        results = []
        for child in doc.children:
            if isinstance(target_type, tuple):
                if isinstance(child, target_type):
                    results.append(child)
            elif element_type.lower().startswith("h"):
                if isinstance(child, HeadingNode) and child.level == int(element_type[1]):
                    results.append(child)
            elif isinstance(child, target_type):
                results.append(child)
        if index is not None and 0 <= index < len(results):
            return [results[index]]
        return results

    @staticmethod
    def analyze_document(doc: DocumentNode) -> dict:
        """分析文档"""
        analyzer = DocumentAnalyzer(doc)
        return analyzer.analyze()

    @staticmethod
    def count_words(text: str) -> int:
        """统计字数"""
        return len(text.split())

    @staticmethod
    def count_chars(text: str) -> int:
        """统计字符数"""
        return len(text)

    @staticmethod
    def length(obj) -> int:
        """获取长度"""
        if obj is None:
            return 0
        if isinstance(obj, (list, str)):
            return len(obj)
        if hasattr(obj, "children"):
            return len(obj.children)
        return 1

    @staticmethod
    def upper(text: str) -> str:
        """转大写"""
        return text.upper()

    @staticmethod
    def lower(text: str) -> str:
        """转小写"""
        return text.lower()

    @staticmethod
    def trim(text: str) -> str:
        """去除首尾空白"""
        return text.strip()

    @staticmethod
    def replace(text: str, old: str, new: str) -> str:
        """文本替换"""
        return text.replace(old, new)

    @staticmethod
    def contains(text: str, sub: str) -> bool:
        """是否包含子串"""
        return sub in text

    @staticmethod
    def starts_with(text: str, prefix: str) -> bool:
        """是否以指定前缀开头"""
        return text.startswith(prefix)

    @staticmethod
    def ends_with(text: str, suffix: str) -> bool:
        """是否以指定后缀结尾"""
        return text.endswith(suffix)

    @staticmethod
    def split(text: str, sep: str = None) -> list:
        """分割字符串"""
        return text.split(sep)

    @staticmethod
    def join(items: list, sep: str = "") -> str:
        """连接列表为字符串"""
        return sep.join(str(i) for i in items)

    @staticmethod
    def range_val(start: int, end: int = None, step: int = 1) -> list:
        """生成范围"""
        if end is None:
            return list(range(int(start)))
        return list(range(int(start), int(end), int(step)))

    @staticmethod
    def abs_val(x) -> float:
        """绝对值"""
        return abs(x)

    @staticmethod
    def min_val(*args):
        """最小值"""
        if len(args) == 1 and hasattr(args[0], "__iter__"):
            return min(args[0])
        return min(args)

    @staticmethod
    def max_val(*args):
        """最大值"""
        if len(args) == 1 and hasattr(args[0], "__iter__"):
            return max(args[0])
        return max(args)

    @staticmethod
    def sum_val(iterable) -> float:
        """求和"""
        return sum(iterable)

    @staticmethod
    def avg(iterable) -> float:
        """平均值"""
        items = list(iterable)
        return sum(items) / len(items) if items else 0

    @staticmethod
    def sort_list(items: list, reverse: bool = False) -> list:
        """排序列表"""
        return sorted(items, reverse=reverse)

    @staticmethod
    def reverse_list(items: list) -> list:
        """反转列表"""
        return list(reversed(items))

    @staticmethod
    def unique(items: list) -> list:
        """去重"""
        seen = []
        for item in items:
            if item not in seen:
                seen.append(item)
        return seen

    @staticmethod
    def first(items: list):
        """获取第一个元素"""
        return items[0] if items else None

    @staticmethod
    def last(items: list):
        """获取最后一个元素"""
        return items[-1] if items else None

    @staticmethod
    def slice_list(items: list, start: int, end: int = None) -> list:
        """切片"""
        return items[start:end]

    @staticmethod
    def type_of(value) -> str:
        """获取类型名称"""
        if value is None:
            return "null"
        return type(value).__name__

    @staticmethod
    def is_empty(value) -> bool:
        """是否为空"""
        if value is None:
            return True
        if isinstance(value, (list, str, dict)):
            return len(value) == 0
        return False

    @staticmethod
    def keys(d: dict) -> list:
        """获取字典键"""
        return list(d.keys())

    @staticmethod
    def values(d: dict) -> list:
        """获取字典值"""
        return list(d.values())


BUILTINS = {
    "load": BuiltinFunctions.load,
    "load_url": BuiltinFunctions.load_url,
    "save": BuiltinFunctions.save,
    "print": BuiltinFunctions.print_value,
    "len": BuiltinFunctions.length,
    "length": BuiltinFunctions.length,
    "count_words": BuiltinFunctions.count_words,
    "count_chars": BuiltinFunctions.count_chars,
    "upper": BuiltinFunctions.upper,
    "lower": BuiltinFunctions.lower,
    "trim": BuiltinFunctions.trim,
    "strip": BuiltinFunctions.trim,
    "replace": BuiltinFunctions.replace,
    "contains": BuiltinFunctions.contains,
    "has": BuiltinFunctions.contains,
    "starts_with": BuiltinFunctions.starts_with,
    "ends_with": BuiltinFunctions.ends_with,
    "split": BuiltinFunctions.split,
    "join": BuiltinFunctions.join,
    "range": BuiltinFunctions.range_val,
    "abs": BuiltinFunctions.abs_val,
    "min": BuiltinFunctions.min_val,
    "max": BuiltinFunctions.max_val,
    "sum": BuiltinFunctions.sum_val,
    "avg": BuiltinFunctions.avg,
    "sort": BuiltinFunctions.sort_list,
    "reverse": BuiltinFunctions.reverse_list,
    "unique": BuiltinFunctions.unique,
    "first": BuiltinFunctions.first,
    "last": BuiltinFunctions.last,
    "slice": BuiltinFunctions.slice_list,
    "type": BuiltinFunctions.type_of,
    "typeof": BuiltinFunctions.type_of,
    "is_empty": BuiltinFunctions.is_empty,
    "keys": BuiltinFunctions.keys,
    "values": BuiltinFunctions.values,
    "extract_links": BuiltinFunctions.extract_links,
    "analyze": BuiltinFunctions.analyze_document,
    "select": BuiltinFunctions.select_elements,
}
