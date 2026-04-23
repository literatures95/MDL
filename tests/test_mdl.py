"""MDL 完整功能测试套件"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import tokenize
from parser import parse
from md_parser import parse_markdown, split_document
from md_generator import generate_markdown
from ast_nodes import (
    BlockquoteNode, CodeBlockNode, DocumentNode, FootnoteDefNode, FootnoteRefNode,
    HeadingNode, HorizontalRuleNode, ImageNode, LinkNode, MathBlockNode,
    MathInlineNode, OrderedListNode, ParagraphNode, TableNode, TaskListNode,
    TextNode, UnorderedListNode,
)
from storage import to_json, from_json
from analyzer import analyze, DocumentAnalyzer
from converter import md_to_html, md_to_text
from interpreter import Interpreter
from mdl_builtins import BuiltinFunctions


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name: str, func):
        """执行单个测试"""
        try:
            func()
            self.passed += 1
            print(f"  [PASS] {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  [FAIL] {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"异常: {type(e).__name__}: {e}"))
            print(f"  [ERROR] {name}: 异常 {type(e).__name__}: {e}")

    def assert_equal(self, actual, expected, msg=""):
        if actual != expected:
            raise AssertionError(f"{msg}\n  期望: {expected!r}\n  实际: {actual!r}")

    def assert_true(self, value, msg=""):
        if not value:
            raise AssertionError(msg or f"期望为 True，实际为 {value!r}")

    def assert_not_none(self, value, msg=""):
        if value is None:
            raise AssertionError(msg or "值不应为 None")

    def assert_type(self, value, expected_type, msg=""):
        if not isinstance(value, expected_type):
            raise AssertionError(f"{msg}\n  期望类型: {expected_type.__name__}\n  实际类型: {type(value).__name__}")

    def summary(self):
        """打印测试总结"""
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"测试结果: {self.passed}/{total} 通过")
        if self.failed > 0:
            print(f"\n[FAIL] 失败的测试 ({self.failed}):")
            for name, err in self.errors:
                print(f"  - {name}: {err}")
        else:
            print("[OK] 所有测试通过!")
        print(f"{'='*50}")
        return self.failed == 0


runner = TestRunner()


def test_lexer_basic():
    """测试词法分析器基础功能"""
    tokens = tokenize('load "test.md" as doc')
    runner.assert_equal(tokens[0].type.name, "LOAD", "load 关键字")
    runner.assert_equal(tokens[1].value, "test.md", "字符串值")
    runner.assert_equal(tokens[2].type.name, "AS", "as 关键字")
    runner.assert_equal(tokens[3].value, "doc", "标识符")


def test_lexer_expressions():
    """测试表达式词法分析"""
    tokens = tokenize("print doc.h1[0]")
    types = [t.type.name for t in tokens]
    runner.assert_true("PRINT" in types, "PRINT 关键字存在")
    runner.assert_true("IDENTIFIER" in types, "标识符存在")


def test_lexer_string_escapes():
    """测试字符串转义"""
    tokens = tokenize('"hello\\nworld"')
    runner.assert_equal(tokens[0].value, "hello\nworld", "换行转义")


def test_parser_load():
    """测试 load 语句解析"""
    program = parse('load "example.md" as mydoc')
    runner.assert_equal(len(program.body), 1, "1条语句")
    stmt = program.body[0]
    runner.assert_equal(stmt.path, "example.md", "文件路径")
    runner.assert_equal(stmt.alias, "mydoc", "别名")


def test_parser_print():
    """测试 print 语句解析"""
    program = parse('print "hello"')
    runner.assert_equal(len(program.body), 1)


def test_parser_save():
    """测试 save 语句解析"""
    program = parse('save as "output.md"')
    runner.assert_equal(len(program.body), 1)


def test_parser_append():
    """测试 append 语句解析"""
    program = parse('append: "新内容"')
    runner.assert_equal(len(program.body), 1)


def test_parser_remove():
    """测试 remove 语句解析"""
    program = parse('remove doc.p[0]')
    runner.assert_true(len(program.body) >= 1, "至少1条语句")


def test_parser_convert():
    """测试 convert 语句解析"""
    program = parse('convert doc to html save as "out.html"')
    runner.assert_equal(len(program.body), 1)
    stmt = program.body[0]
    runner.assert_equal(stmt.target_format, "html", "目标格式")


def test_md_parse_heading():
    """测试 Markdown 标题解析"""
    doc = parse_markdown("# 一级标题\n\n## 二级标题\n\n### 三级标题")
    headings = [c for c in doc.children if isinstance(c, HeadingNode)]
    runner.assert_true(len(headings) >= 2, "至少2个标题")
    runner.assert_equal(headings[0].level, 1, "H1级别")
    runner.assert_equal(headings[0].raw_text, "一级标题", "H1文本")


def test_md_parse_paragraph():
    """测试 Markdown 段落解析"""
    doc = parse_markdown("这是一个普通段落。\n\n这是另一个段落。")
    paragraphs = [c for c in doc.children if isinstance(c, ParagraphNode)]
    runner.assert_equal(len(paragraphs), 2, "2个段落")


def test_md_parse_bold_italic():
    """测试粗体斜体解析"""
    doc = parse_markdown("**粗体** 和 *斜体* 和 ***粗斜体*** ~~删除线~~")
    p = doc.children[0]
    content_types = [n.node_type.name for n in p.content]
    runner.assert_true("BOLD" in content_types, "包含粗体节点")
    runner.assert_true("ITALIC" in content_types, "包含斜体节点")
    runner.assert_true("STRIKETHROUGH" in content_types, "包含删除线节点")


def test_md_parse_code_block():
    """测试代码块解析"""
    source = '```python\ndef hello():\n    print("Hello")\n```'
    doc = parse_markdown(source)
    code_blocks = [c for c in doc.children if isinstance(c, CodeBlockNode)]
    runner.assert_equal(len(code_blocks), 1, "1个代码块")
    cb = code_blocks[0]
    runner.assert_equal(cb.language, "python", "语言标识")
    runner.assert_true("def hello" in cb.code, "代码内容")


def test_md_parse_list():
    """测试列表解析"""
    source = "- 项目一\n- 项目二\n- 项目三"
    doc = parse_markdown(source)
    lists = [c for c in doc.children if isinstance(c, UnorderedListNode)]
    runner.assert_equal(len(lists), 1, "1个列表")
    ul = lists[0]
    runner.assert_equal(len(ul.items), 3, "3个列表项")


def test_md_parse_ordered_list():
    """测试有序列表解析"""
    source = "1. 第一项\n2. 第二项\n3. 第三项"
    doc = parse_markdown(source)
    ols = [c for c in doc.children if isinstance(c, OrderedListNode)]
    ol = ols[0]
    runner.assert_equal(len(ol.items), 3, "3个有序项")
    runner.assert_equal(ol.start, 1, "起始编号")


def test_md_parse_task_list():
    """测试任务列表解析"""
    source = "- [x] 已完成任务\n- [ ] 未完成任务\n- [x] 另一个已完成"
    doc = parse_markdown(source)
    tasks = [c for c in doc.children if isinstance(c, TaskListNode)]
    tl = tasks[0]
    runner.assert_true(tl.items[0].checked, "第1项已完成")
    runner.assert_true(not tl.items[1].checked, "第2项未完成")
    runner.assert_true(tl.items[2].checked, "第3项已完成")


def test_md_parse_link_image():
    """测试链接和图片解析"""
    source = "[链接文字](https://example.com) ![图片](image.png)"
    doc = parse_markdown(source)
    p = doc.children[0]
    has_link = any(isinstance(n, LinkNode) for n in p.content)
    has_img = any(isinstance(n, ImageNode) for n in p.content)
    runner.assert_true(has_link, "包含链接节点")
    runner.assert_true(has_img, "包含图片节点")


def test_md_parse_table():
    """测试表格解析"""
    source = "| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| A | B | C |\n| D | E | F |"
    doc = parse_markdown(source)
    tables = [c for c in doc.children if isinstance(c, TableNode)]
    table = tables[0]
    headers = [c.content.strip() for c in table.headers if c.content.strip()]
    runner.assert_equal(len(headers), 3, "3列(过滤空)")


def test_md_parse_blockquote():
    """测试引用块解析"""
    source = "> 这是一段引用\n> 可以多行"
    doc = parse_markdown(source)
    bqs = [c for c in doc.children if isinstance(c, BlockquoteNode)]
    runner.assert_equal(len(bqs), 1, "1个引用块")


def test_md_parse_horizontal_rule():
    """测试分隔线解析"""
    doc = parse_markdown("---\n\n***\n\n___")
    hrs = [c for c in doc.children if isinstance(c, HorizontalRuleNode)]
    runner.assert_equal(len(hrs), 3, "3条分隔线")


def test_md_parse_superscript_subscript():
    """测试上标下标解析"""
    doc = parse_markdown("H~2~O 和 E=mc^2^")
    p = doc.children[0]
    content_types = [n.node_type.name for n in p.content]
    runner.assert_true("SUBSCRIPT" in content_types, "包含下标节点")
    runner.assert_true("SUPERSCRIPT" in content_types, "包含上标节点")


def test_md_parse_math():
    """测试数学公式解析"""
    doc = parse_markdown("行内公式 $E=mc^2$ 和块级公式\n\n$$\n\\int f(x)dx\n$$")
    p = doc.children[0]
    has_inline_math = any(isinstance(n, MathInlineNode) for n in p.content)
    runner.assert_true(has_inline_math, "包含行内数学公式")
    has_block_math = any(isinstance(c, MathBlockNode) for c in doc.children)
    runner.assert_true(has_block_math, "包含块级数学公式")


def test_md_parse_footnote():
    """测试脚注解析"""
    doc = parse_markdown("这是一个脚注[^1]。\n\n[^1]: 这是脚注内容")
    p = doc.children[0]
    has_ref = any(isinstance(n, FootnoteRefNode) for n in p.content)
    runner.assert_true(has_ref, "包含脚注引用")
    has_def = any(isinstance(c, FootnoteDefNode) for c in doc.children)
    runner.assert_true(has_def, "包含脚注定义")


def test_md_generate_heading():
    """测试标题生成"""
    h = HeadingNode(level=2, content=[TextNode(value="测试标题")], raw_text="测试标题")
    result = generate_markdown(DocumentNode(children=[h]))
    runner.assert_true("## 测试标题" in result, "H2生成正确")


def test_md_generate_paragraph():
    """测试段落生成"""
    p = ParagraphNode(content=[TextNode(value="测试段落")], raw_text="测试段落")
    result = generate_markdown(DocumentNode(children=[p]))
    runner.assert_true("测试段落" in result, "段落生成正确")


def test_md_roundtrip():
    """测试解析→生成的往返一致性"""
    original = "# 标题\n\n这是一段**粗体**文字。\n\n- 列表项1\n- 列表项2\n\n```python\ncode\n```"
    doc = parse_markdown(original)
    generated = generate_markdown(doc)
    runner.assert_true("# 标题" in generated, "往返保留标题")
    runner.assert_true("**粗体**" in generated, "往返保留粗体")
    runner.assert_true("- 列表项1" in generated, "往返保留列表")


def test_storage_split():
    """测试文档拆分"""
    source = "# 标题\n\n段落内容\n\n```python\ncode\n```"
    doc = parse_markdown(source)
    result = split_document(doc)
    runner.assert_true(len(result["headings"]) > 0, "有标题")
    runner.assert_true(len(result["paragraphs"]) > 0, "有段落")
    runner.assert_true(len(result["code_blocks"]) > 0, "有代码块")


def test_storage_json_export_import():
    """测试 JSON 导出导入"""
    source = "# 测试文档\n\n## 子标题\n\n段落内容"
    doc = parse_markdown(source)
    json_data = to_json(doc)
    restored = from_json(json_data)
    runner.assert_true(len(restored.children) > 0, "恢复后文档非空")


def test_analyzer_overview():
    """测试分析器概览"""
    source = "# 标题\n\n这是一个测试段落，包含一些中文和English单词。\n\n**重点内容**"
    doc = parse_markdown(source)
    result = analyze(doc)
    runner.assert_true("overview" in result, "概览存在")
    runner.assert_true(result["overview"]["total_elements"] >= 2, "至少2个元素")


def test_analyzer_headings():
    """测试标题分析"""
    source = "# 一级\n\n## 二级A\n\n## 二级B"
    doc = parse_markdown(source)
    a = DocumentAnalyzer(doc)
    h = a.analyze_headings()
    runner.assert_true(h["count"] >= 3, "至少3个标题")


def test_converter_html():
    """测试 HTML 转换"""
    source = "# 标题\n\n段落 **粗体** 文字"
    html = md_to_html(source, full_page=False)
    runner.assert_true("<h1>" in html, "包含h1标签")
    runner.assert_true("<strong>" in html, "包含strong标签")


def test_converter_text():
    """测试纯文本转换"""
    source = "# 标题\n\n段落文字"
    text = md_to_text(source)
    runner.assert_true("标题" in text, "包含标题文本")


def test_interpreter_eval():
    """测试解释器基本求值"""
    interp = Interpreter()
    result = interp.run_script('print "Hello MDL"')
    runner.assert_not_none(result, "执行成功")


def test_interpreter_load():
    """测试解释器加载文档"""
    interp = Interpreter()
    source = '# 一级标题\n\n段落内容'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_path = os.path.join(base_dir, "_temp_test.md")
    temp_path = os.path.normpath(temp_path)
    temp_path_unix = temp_path.replace("\\", "/")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(source)
    try:
        doc = interp.run_script(f'load "{temp_path_unix}"')
        runner.assert_not_none(doc, "加载成功")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_builtin_functions():
    """测试内置函数"""
    runner.assert_equal(BuiltinFunctions.upper("hello"), "HELLO", "大写转换")
    runner.assert_equal(BuiltinFunctions.lower("WORLD"), "world", "小写转换")
    runner.assert_equal(BuiltinFunctions.trim("  hello  "), "hello", "去除空白")
    runner.assert_equal(BuiltinFunctions.length([1, 2, 3]), 3, "列表长度")
    runner.assert_equal(BuiltinFunctions.contains("hello world", "world"), True, "包含判断")
    runner.assert_equal(BuiltinFunctions.split("a,b,c", ","), ["a", "b", "c"], "分割字符串")
    runner.assert_equal(BuiltinFunctions.join(["a", "b", "c"], "-"), "a-b-c", "连接字符串")


def test_format_converter():
    """测试格式转换器"""
    from formats import FormatConverter
    html = "<h1>标题</h1><p>段落</p>"
    md = FormatConverter.html_to_markdown(html)
    runner.assert_true("# 标题" in md, "HTML转Markdown: 标题")
    runner.assert_true("段落" in md, "HTML转Markdown: 段落")


def test_cleaner():
    """测试文档清理器"""
    from cleaner import clean_document
    dirty = "# 标题\n\n\n\n段落\n\n\n\n"
    clean = clean_document(dirty)
    runner.assert_true(clean.count("\n\n\n") == 0, "移除多余空行")


def test_extractor():
    """测试结构化提取器"""
    from extractor import extract_structured
    md = "# 文档标题\n\n## 第一章\n\n段落内容\n\n[链接](http://example.com)"
    result = extract_structured(md, "basic")
    runner.assert_true("title" in result, "提取标题")
    runner.assert_true("headings" in result, "提取标题列表")
    runner.assert_true("links" in result, "提取链接")


def test_image_extractor():
    """测试图片提取器"""
    from image_extractor import ImageExtractor
    md = "![图片1](image1.png) 和 ![图片2](image2.jpg)"
    images = ImageExtractor.extract_images(md)
    runner.assert_equal(len(images), 2, "提取图片数量")
    runner.assert_equal(images[0]["alt"], "图片1", "图片alt属性")


def test_llm_enhancer():
    """测试 LLM 增强器"""
    from llm_enhancer import LLMEnhancer, LLMConfig
    config = LLMConfig(provider="openai", model="gpt-3.5-turbo")
    enhancer = LLMEnhancer(config)
    runner.assert_true(hasattr(enhancer, "enhance_text"), "LLM 增强器方法存在")
    runner.assert_true(hasattr(enhancer, "enhance_markdown"), "LLM Markdown 增强方法存在")


def test_batch_config():
    """测试批量处理配置"""
    from batch import BatchConfig, BatchProcessor
    config = BatchConfig(max_workers=2, use_multiprocessing=False)
    processor = BatchProcessor(config)
    runner.assert_equal(processor.config.max_workers, 2, "批量处理配置正确")


def test_epub_mobi_support():
    """测试 EPUB/MOBI 支持"""
    from formats import FORMATS
    runner.assert_true("epub" in FORMATS, "EPUB 格式已注册")
    runner.assert_true("mobi" in FORMATS, "MOBI 格式已注册")


def test_image_format_support():
    """测试图像格式支持"""
    from formats import ImageConverter, FORMATS
    runner.assert_true("png" in FORMATS, "PNG 格式已注册")
    runner.assert_true("jpg" in FORMATS, "JPG 格式已注册")
    runner.assert_true("gif" in FORMATS, "GIF 格式已注册")
    runner.assert_true(hasattr(ImageConverter, "is_available"), "图像转换器可用检查方法存在")
    runner.assert_true(hasattr(ImageConverter, "is_ocr_available"), "OCR 可用检查方法存在")


def test_latex_converter():
    """测试 LaTeX 转换器"""
    from formats import LaTeXConverter
    latex = r"\section{标题}\subsection{子标题}\textbf{粗体}\textit{斜体}"
    md = LaTeXConverter.to_markdown(latex)
    runner.assert_true("## 标题" in md, "LaTeX section 转换")
    runner.assert_true("### 子标题" in md, "LaTeX subsection 转换")
    runner.assert_true("**粗体**" in md, "LaTeX textbf 转换")
    runner.assert_true("*斜体*" in md, "LaTeX textit 转换")


def test_orgmode_converter():
    """测试 Org-mode 转换器"""
    from formats import OrgModeConverter
    org = "* 一级标题\n** 二级标题\n**粗体**\n/斜体/\n=代码="
    md = OrgModeConverter.to_markdown(org)
    runner.assert_true("# 一级标题" in md or "## 一级标题" in md, "Org 标题转换")
    runner.assert_true("**粗体**" in md, "Org 粗体转换")
    runner.assert_true("*斜体*" in md, "Org 斜体转换")


def test_mediawiki_converter():
    """测试 MediaWiki 转换器"""
    from formats import MediaWikiConverter
    wiki = "== 标题 ==\n'''粗体'''\n''斜体''\n[[链接|显示文本]]"
    md = MediaWikiConverter.to_markdown(wiki)
    runner.assert_true("**粗体**" in md, "Wiki 粗体转换")
    runner.assert_true("*斜体*" in md, "Wiki 斜体转换")
    runner.assert_true("[显示文本](链接)" in md, "Wiki 链接转换")


def test_xml_converter():
    """测试 XML 转换器"""
    from formats import XMLConverter
    xml = '<root><item>内容</item></root>'
    md = XMLConverter.to_markdown(xml)
    runner.assert_true("root" in md, "XML 根元素转换")
    runner.assert_true("item" in md, "XML 子元素转换")


def test_yaml_converter():
    """测试 YAML 转换器"""
    from formats import YAMLConverter
    yaml_content = "title: 测试\nauthor: 作者\nitems:\n  - a\n  - b"
    md = YAMLConverter.to_markdown(yaml_content)
    runner.assert_true("title" in md or "测试" in md, "YAML 转换包含内容")


def test_toml_converter():
    """测试 TOML 转换器"""
    from formats import TOMLConverter
    toml_content = 'title = "测试"\nauthor = "作者"'
    md = TOMLConverter.to_markdown(toml_content)
    runner.assert_true("title" in md or "测试" in md, "TOML 转换包含内容")


def test_tsv_converter():
    """测试 TSV 转换器"""
    from formats import TSVConverter
    tsv = "姓名\t年龄\n张三\t25\n李四\t30"
    md = TSVConverter.to_markdown(tsv)
    runner.assert_true("|" in md, "TSV 转换为表格")
    runner.assert_true("姓名" in md, "TSV 包含表头")


def test_metadata_extraction():
    """测试元数据提取"""
    from formats import extract_metadata, DocumentMetadata
    runner.assert_true(callable(extract_metadata), "元数据提取函数存在")
    metadata = DocumentMetadata(title="测试", author="作者")
    runner.assert_equal(metadata.title, "测试", "元数据标题正确")
    runner.assert_equal(metadata.author, "作者", "元数据作者正确")


def test_format_categories():
    """测试格式分类"""
    from formats import get_formats_by_category
    categories = get_formats_by_category()
    runner.assert_true("document" in categories, "文档类别存在")
    runner.assert_true("image" in categories, "图像类别存在")
    runner.assert_true("data" in categories, "数据类别存在")


def test_convert_with_metadata():
    """测试带元数据的转换"""
    from formats import convert_with_metadata
    runner.assert_true(callable(convert_with_metadata), "带元数据转换函数存在")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("[TEST] MDL 功能测试套件")
    print("=" * 50)

    print("\n--- 词法分析器 ---")
    runner.test("基础词法分析", test_lexer_basic)
    runner.test("表达式词法分析", test_lexer_expressions)
    runner.test("字符串转义", test_lexer_string_escapes)

    print("\n--- MDL 解析器 ---")
    runner.test("load 语句", test_parser_load)
    runner.test("print 语句", test_parser_print)
    runner.test("save 语句", test_parser_save)
    runner.test("append 语句", test_parser_append)
    runner.test("remove 语句", test_parser_remove)
    runner.test("convert 语句", test_parser_convert)

    print("\n--- Markdown 解析引擎 ---")
    runner.test("标题解析", test_md_parse_heading)
    runner.test("段落解析", test_md_parse_paragraph)
    runner.test("粗体/斜体解析", test_md_parse_bold_italic)
    runner.test("代码块解析", test_md_parse_code_block)
    runner.test("无序列表解析", test_md_parse_list)
    runner.test("有序列表解析", test_md_parse_ordered_list)
    runner.test("任务列表解析", test_md_parse_task_list)
    runner.test("链接/图片解析", test_md_parse_link_image)
    runner.test("表格解析", test_md_parse_table)
    runner.test("引用块解析", test_md_parse_blockquote)
    runner.test("分隔线解析", test_md_parse_horizontal_rule)
    runner.test("上标/下标解析", test_md_parse_superscript_subscript)
    runner.test("数学公式解析", test_md_parse_math)
    runner.test("脚注解析", test_md_parse_footnote)

    print("\n--- Markdown 生成器 ---")
    runner.test("标题生成", test_md_generate_heading)
    runner.test("段落生成", test_md_generate_paragraph)
    runner.test("往返一致性", test_md_roundtrip)

    print("\n--- 存储引擎 ---")
    runner.test("文档拆分", test_storage_split)
    runner.test("JSON 导出导入", test_storage_json_export_import)

    print("\n--- 分析引擎 ---")
    runner.test("文档概览", test_analyzer_overview)
    runner.test("标题分析", test_analyzer_headings)

    print("\n--- 转换器 ---")
    runner.test("HTML 转换", test_converter_html)
    runner.test("纯文本转换", test_converter_text)

    print("\n--- 解释器 ---")
    runner.test("基本求值", test_interpreter_eval)
    runner.test("加载文档", test_interpreter_load)

    print("\n--- 内置函数 ---")
    runner.test("内置函数库", test_builtin_functions)

    print("\n--- 新功能模块 ---")
    runner.test("格式转换器", test_format_converter)
    runner.test("文档清理器", test_cleaner)
    runner.test("结构化提取器", test_extractor)
    runner.test("图片提取器", test_image_extractor)
    runner.test("LLM 增强器", test_llm_enhancer)
    runner.test("批量处理配置", test_batch_config)
    runner.test("EPUB/MOBI 支持", test_epub_mobi_support)

    print("\n--- 多格式支持 ---")
    runner.test("图像格式支持", test_image_format_support)
    runner.test("LaTeX 转换器", test_latex_converter)
    runner.test("Org-mode 转换器", test_orgmode_converter)
    runner.test("MediaWiki 转换器", test_mediawiki_converter)
    runner.test("XML 转换器", test_xml_converter)
    runner.test("YAML 转换器", test_yaml_converter)
    runner.test("TOML 转换器", test_toml_converter)
    runner.test("TSV 转换器", test_tsv_converter)
    runner.test("元数据提取", test_metadata_extraction)
    runner.test("格式分类", test_format_categories)
    runner.test("带元数据转换", test_convert_with_metadata)

    return runner.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
