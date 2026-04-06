"""MDL AST 节点定义 - 所有 Markdown 元素和 MDL 语法节点的完整类型系统"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum, auto


class NodeType(Enum):
    """节点类型枚举 - 覆盖所有 Markdown 元素"""

    DOCUMENT = auto()
    HEADING = auto()
    PARAGRAPH = auto()
    TEXT = auto()
    BOLD = auto()
    ITALIC = auto()
    BOLD_ITALIC = auto()
    STRIKETHROUGH = auto()
    SUPERSCRIPT = auto()
    SUBSCRIPT = auto()
    CODE_INLINE = auto()
    CODE_BLOCK = auto()
    BLOCKQUOTE = auto()
    HORIZONTAL_RULE = auto()
    UNORDERED_LIST = auto()
    ORDERED_LIST = auto()
    LIST_ITEM = auto()
    TASK_LIST = auto()
    TASK_ITEM = auto()
    LINK = auto()
    IMAGE = auto()
    TABLE = auto()
    TABLE_ROW = auto()
    TABLE_CELL = auto()
    HTML_BLOCK = auto()
    HTML_INLINE = auto()
    LINE_BREAK = auto()
    SOFT_BREAK = auto()
    FOOTNOTE_REF = auto()
    FOOTNOTE_DEF = auto()
    DEFINITION_LIST = auto()
    DEFINITION_ITEM = auto()
    MATH_INLINE = auto()
    MATH_BLOCK = auto()

    MDL_PROGRAM = auto()
    MDL_LOAD = auto()
    MDL_SAVE = auto()
    MDL_PRINT = auto()
    MDL_SET = auto()
    MDL_INSERT = auto()
    MDL_APPEND = auto()
    MDL_REMOVE = auto()
    MDL_CONVERT = auto()
    MDL_FOR = auto()
    MDL_IF = auto()
    MDL_FUNC_DEF = auto()
    MDL_FUNC_CALL = auto()
    MDL_ASSIGN = auto()
    MDL_IDENTIFIER = auto()
    MDL_STRING = auto()
    MDL_NUMBER = auto()
    MDL_BOOLEAN = auto()
    MDL_SELECTOR = auto()
    MDL_INDEX = auto()
    MDL_PROPERTY = auto()
    MDL_BINARY_OP = auto()
    MDL_UNARY_OP = auto()
    MDL_COMPARISON = auto()

    MDL_BATCH = auto()
    MDL_CLEAN = auto()
    MDL_EXTRACT = auto()
    MDL_TRANSFORM = auto()
    MDL_LIST = auto()
    MDL_ARRAY = auto()


@dataclass
class ASTNode:
    """AST 基础节点"""
    node_type: NodeType = field(default=None, repr=False)
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict:
        result = {"type": self.node_type.name}
        for k, v in self.__dict__.items():
            if k == "node_type":
                continue
            if isinstance(v, ASTNode):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                result[k] = v
        return result


@dataclass
class DocumentNode(ASTNode):
    """文档根节点 - 包含所有顶层元素"""
    children: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.DOCUMENT


@dataclass
class HeadingNode(ASTNode):
    """标题节点 H1-H6"""
    level: int = 1
    content: list = field(default_factory=list)
    raw_text: str = ""

    def __post_init__(self):
        self.node_type = NodeType.HEADING


@dataclass
class ParagraphNode(ASTNode):
    """段落节点 - 包含内联元素"""
    content: list = field(default_factory=list)
    raw_text: str = ""

    def __post_init__(self):
        self.node_type = NodeType.PARAGRAPH


@dataclass
class TextNode(ASTNode):
    """纯文本节点"""
    value: str = ""

    def __post_init__(self):
        self.node_type = NodeType.TEXT


@dataclass
class BoldNode(ASTNode):
    """粗体文本节点"""
    content: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.BOLD


@dataclass
class ItalicNode(ASTNode):
    """斜体文本节点"""
    content: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.ITALIC


@dataclass
class BoldItalicNode(ASTNode):
    """粗斜体文本节点"""
    content: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.BOLD_ITALIC


@dataclass
class StrikethroughNode(ASTNode):
    """删除线文本节点"""
    content: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.STRIKETHROUGH


@dataclass
class CodeInlineNode(ASTNode):
    """行内代码节点"""
    code: str = ""
    language: str = ""

    def __post_init__(self):
        self.node_type = NodeType.CODE_INLINE


@dataclass
class CodeBlockNode(ASTNode):
    """代码块节点"""
    code: str = ""
    language: str = ""
    fenced: bool = True

    def __post_init__(self):
        self.node_type = NodeType.CODE_BLOCK


@dataclass
class BlockquoteNode(ASTNode):
    """引用块节点"""
    content: list = field(default_factory=list)
    level: int = 1

    def __post_init__(self):
        self.node_type = NodeType.BLOCKQUOTE


@dataclass
class HorizontalRuleNode(ASTNode):
    """分隔线节点"""
    style: str = "***"

    def __post_init__(self):
        self.node_type = NodeType.HORIZONTAL_RULE


@dataclass
class UnorderedListNode(ASTNode):
    """无序列表节点"""
    items: list = field(default_factory=list)
    marker: str = "-"

    def __post_init__(self):
        self.node_type = NodeType.UNORDERED_LIST


@dataclass
class OrderedListNode(ASTNode):
    """有序列表节点"""
    items: list = field(default_factory=list)
    start: int = 1
    marker: str = "."

    def __post_init__(self):
        self.node_type = NodeType.ORDERED_LIST


@dataclass
class ListItemNode(ASTNode):
    """列表项节点"""
    content: list = field(default_factory=list)
    checked: Optional[bool] = None

    def __post_init__(self):
        self.node_type = NodeType.LIST_ITEM


@dataclass
class TaskListNode(ASTNode):
    """任务列表节点"""
    items: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.TASK_LIST


@dataclass
class TaskItemNode(ASTNode):
    """任务项节点"""
    content: list = field(default_factory=list)
    checked: bool = False

    def __post_init__(self):
        self.node_type = NodeType.TASK_ITEM


@dataclass
class LinkNode(ASTNode):
    """链接节点"""
    text: str = ""
    url: str = ""
    title: str = ""

    def __post_init__(self):
        self.node_type = NodeType.LINK


@dataclass
class ImageNode(ASTNode):
    """图片节点"""
    alt: str = ""
    src: str = ""
    title: str = ""

    def __post_init__(self):
        self.node_type = NodeType.IMAGE


@dataclass
class TableNode(ASTNode):
    """表格节点"""
    headers: list = field(default_factory=list)
    rows: list = field(default_factory=list)
    alignments: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.TABLE


@dataclass
class TableRowNode(ASTNode):
    """表格行节点"""
    cells: list = field(default_factory=list)
    is_header: bool = False

    def __post_init__(self):
        self.node_type = NodeType.TABLE_ROW


@dataclass
class TableCellNode(ASTNode):
    """表格单元格节点"""
    content: str = ""
    alignment: str = ""

    def __post_init__(self):
        self.node_type = NodeType.TABLE_CELL


@dataclass
class HTMLBlockNode(ASTNode):
    """HTML 块级节点"""
    html: str = ""
    tag: str = ""

    def __post_init__(self):
        self.node_type = NodeType.HTML_BLOCK


@dataclass
class HTMLInlineNode(ASTNode):
    """HTML 行内节点"""
    html: str = ""

    def __post_init__(self):
        self.node_type = NodeType.HTML_INLINE


@dataclass
class LineBreakNode(ASTNode):
    """硬换行节点（两个空格+换行或反斜杠）"""

    def __post_init__(self):
        self.node_type = NodeType.LINE_BREAK


@dataclass
class SoftBreakNode(ASTNode):
    """软换行节点（单个换行）"""

    def __post_init__(self):
        self.node_type = NodeType.SOFT_BREAK


@dataclass
class SuperscriptNode(ASTNode):
    """上标节点 ^文本^"""
    content: str = ""

    def __post_init__(self):
        self.node_type = NodeType.SUPERSCRIPT


@dataclass
class SubscriptNode(ASTNode):
    """下标节点 ~文本~"""
    content: str = ""

    def __post_init__(self):
        self.node_type = NodeType.SUBSCRIPT


@dataclass
class FootnoteRefNode(ASTNode):
    """脚注引用节点 [^id]"""
    ref_id: str = ""

    def __post_init__(self):
        self.node_type = NodeType.FOOTNOTE_REF


@dataclass
class FootnoteDefNode(ASTNode):
    """脚注定义节点 [^id]: 内容"""
    ref_id: str = ""
    content: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.FOOTNOTE_DEF


@dataclass
class DefinitionListNode(ASTNode):
    """定义列表节点"""
    items: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.DEFINITION_LIST


@dataclass
class DefinitionItemNode(ASTNode):
    """定义项节点"""
    term: str = ""
    definitions: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.DEFINITION_ITEM


@dataclass
class MathInlineNode(ASTNode):
    """行内数学公式节点 $公式$"""
    formula: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MATH_INLINE


@dataclass
class MathBlockNode(ASTNode):
    """块级数学公式节点 $$公式$$"""
    formula: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MATH_BLOCK


@dataclass
class MDLProgramNode(ASTNode):
    """MDL 程序根节点"""
    body: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_PROGRAM


@dataclass
class MDLLoadNode(ASTNode):
    """加载文件语句"""
    path: str = ""
    alias: str = "doc"
    encoding: str = "utf-8"

    def __post_init__(self):
        self.node_type = NodeType.MDL_LOAD


@dataclass
class MDLSaveNode(ASTNode):
    """保存文件语句"""
    target: str = "doc"
    path: str = ""
    encoding: str = "utf-8"

    def __post_init__(self):
        self.node_type = NodeType.MDL_SAVE


@dataclass
class MDLPrintNode(ASTNode):
    """打印语句"""
    expression: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_PRINT


@dataclass
class MDLSetNode(ASTNode):
    """赋值/设置语句"""
    target: Any = None
    value: Any = None
    property_name: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_SET


@dataclass
class MDLInsertNode(ASTNode):
    """插入语句"""
    target: Any = None
    position: str = "after"
    content: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_INSERT


@dataclass
class MDLAppendNode(ASTNode):
    """追加语句"""
    target: str = "doc"
    content: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_APPEND


@dataclass
class MDLRemoveNode(ASTNode):
    """删除语句"""
    target: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_REMOVE


@dataclass
class MDLConvertNode(ASTNode):
    """转换语句"""
    source: Any = None
    target_format: str = "html"
    output_path: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_CONVERT


@dataclass
class MDLForNode(ASTNode):
    """循环语句"""
    var_name: str = ""
    iterable: Any = None
    body: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_FOR


@dataclass
class MDLIfNode(ASTNode):
    """条件语句"""
    condition: Any = None
    then_body: list = field(default_factory=list)
    else_body: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_IF


@dataclass
class MDLFuncDefNode(ASTNode):
    """函数定义"""
    name: str = ""
    params: list = field(default_factory=list)
    body: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_FUNC_DEF


@dataclass
class MDLFuncCallNode(ASTNode):
    """函数调用"""
    name: str = ""
    args: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_FUNC_CALL


@dataclass
class MDLAssignNode(ASTNode):
    """变量赋值"""
    name: str = ""
    value: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_ASSIGN


@dataclass
class MDLIdentifierNode(ASTNode):
    """标识符"""
    name: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_IDENTIFIER


@dataclass
class MDLStringNode(ASTNode):
    """字符串字面量"""
    value: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_STRING


@dataclass
class MDLNumberNode(ASTNode):
    """数字字面量"""
    value: float = 0.0

    def __post_init__(self):
        self.node_type = NodeType.MDL_NUMBER


@dataclass
class MDLBooleanNode(ASTNode):
    """布尔值字面量"""
    value: bool = False

    def __post_init__(self):
        self.node_type = NodeType.MDL_BOOLEAN


@dataclass
class MDLSelectorNode(ASTNode):
    """选择器节点 - 用于选取 Markdown 元素"""
    element_type: str = ""
    index: Optional[int] = None
    filters: dict = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.MDL_SELECTOR


@dataclass
class MDLIndexNode(ASTNode):
    """索引访问节点"""
    object_node: Any = None
    index: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_INDEX


@dataclass
class MDLPropertyNode(ASTNode):
    """属性访问节点"""
    object_node: Any = None
    property_name: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_PROPERTY


@dataclass
class MDLBinaryOpNode(ASTNode):
    """二元运算符节点"""
    operator: str = ""
    left: Any = None
    right: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_BINARY_OP


@dataclass
class MDLUnaryOpNode(ASTNode):
    """一元运算符节点"""
    operator: str = ""
    operand: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_UNARY_OP


@dataclass
class MDLComparisonNode(ASTNode):
    """比较运算符节点"""
    operator: str = ""
    left: Any = None
    right: Any = None

    def __post_init__(self):
        self.node_type = NodeType.MDL_COMPARISON


@dataclass
class MDLBatchNode(ASTNode):
    """批量处理语句"""
    input_patterns: list = field(default_factory=list)
    output_dir: str = ""
    output_format: str = "markdown"
    options: dict = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.MDL_BATCH


@dataclass
class MDLCleanNode(ASTNode):
    """文档清理语句"""
    target: Any = None
    options: dict = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.MDL_CLEAN


@dataclass
class MDLExtractNode(ASTNode):
    """结构化提取语句"""
    target: Any = None
    schema: str = "basic"
    output_path: str = ""

    def __post_init__(self):
        self.node_type = NodeType.MDL_EXTRACT


@dataclass
class MDLTransformNode(ASTNode):
    """格式转换语句"""
    source: Any = None
    source_format: str = ""
    target_format: str = "markdown"
    options: dict = field(default_factory=dict)

    def __post_init__(self):
        self.node_type = NodeType.MDL_TRANSFORM


@dataclass
class MDLListNode(ASTNode):
    """列表字面量"""
    elements: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_LIST


@dataclass
class MDLArrayNode(ASTNode):
    """数组节点 (列表的别名)"""
    elements: list = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MDL_ARRAY
