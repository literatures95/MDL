# MDL - Markdown 操作语言

MDL (Markdown Operation Language) 是一个专门为 Markdown 文档操作设计的领域特定语言 (DSL)，提供完美的 Markdown 解析、修改、转换和分析功能。

## 项目进度

| 阶段 | 状态 | 说明 |
|------|------|------|
| 设计方案 | 完成 | 完整的语言设计文档 |
| 核心引擎 | 完成 | 词法分析、语法解析、解释器 |
| Markdown 处理 | 完成 | 解析、生成、转换 |
| 存储与分析 | 完成 | 文档拆分、统计分析 |
| 扩展语法 | 完成 | 上标下标、脚注、数学公式 |
| 多格式支持 | 完成 | 25+ 种格式支持 |
| 高级功能 | 完成 | 批量处理、文档清理、结构化提取 |
| LLM 增强 | 完成 | OpenAI/Anthropic/Ollama 支持 |
| CLI 工具 | 完成 | 完整的命令行界面 |
| 测试验证 | 完成 | 53/53 测试通过 |

## 项目统计

| 指标 | 数据 |
|------|------|
| Python 文件 | 19 个 |
| 总代码行数 | 9,000+ 行 |
| 测试用例 | 53 个 |
| AST 节点类型 | 50+ 种 |
| 支持 Markdown 元素 | 20+ 种 |
| 支持输入格式 | 25+ 种 |
| LLM 提供者 | 3 种 |

## 功能特性

### 1. 完整的 Markdown 解析

| 元素 | 语法 | 示例 |
|------|------|------|
| 标题 | `# ~ ######` | `# 一级标题` |
| 粗体 | `**文本**` | **粗体** |
| 斜体 | `*文本*` | *斜体* |
| 删除线 | `~~文本~~` | ~~删除线~~ |
| 上标 | `^文本^` | `x^2^` → x² |
| 下标 | `~文本~` | `H~2~O` → H₂O |
| 行内代码 | `` `代码` `` | `code` |
| 代码块 | ` ```语言 ` | 见下方示例 |
| 无序列表 | `- 项目` | 见下方示例 |
| 有序列表 | `1. 项目` | 见下方示例 |
| 任务列表 | `- [x] 任务` | 见下方示例 |
| 表格 | `\| 列1 \| 列2 \|` | 见下方示例 |
| 链接 | `[文字](URL)` | [链接](url) |
| 图片 | `![alt](URL)` | 图片 |
| 引用块 | `> 引用` | 引用 |
| 分隔线 | `---` | 水平线 |
| 脚注 | `[^id]` | 脚注引用 |
| 数学公式 | `$公式$` | 行内/块级公式 |
| 定义列表 | `术语\n: 定义` | 定义列表 |
| 段内换行 | 行末两空格 | 硬换行 |

### 2. 多格式支持

#### 文档格式

| 格式 | 输入 | 输出 | 依赖包 |
|------|:----:|:----:|--------|
| Markdown (.md) | ✅ | ✅ | 内置 |
| HTML (.html) | ✅ | ✅ | 内置 |
| 纯文本 (.txt) | ✅ | ✅ | 内置 |
| reStructuredText (.rst) | ✅ | ✅ | 内置 |
| LaTeX (.tex) | ✅ | ✅ | 内置 |
| Org-mode (.org) | ✅ | ✅ | 内置 |
| MediaWiki (.wiki) | ✅ | ✅ | 内置 |

#### 数据格式

| 格式 | 输入 | 输出 | 依赖包 |
|------|:----:|:----:|--------|
| JSON (.json) | ✅ | ✅ | 内置 |
| CSV (.csv) | ✅ | ✅ | 内置 |
| TSV (.tsv) | ✅ | ✅ | 内置 |
| XML (.xml) | ✅ | ✅ | 内置 |
| YAML (.yaml) | ✅ | ✅ | pyyaml |
| TOML (.toml) | ✅ | ✅ | toml |

#### 办公文档

| 格式 | 输入 | 输出 | 依赖包 |
|------|:----:|:----:|--------|
| PDF (.pdf) | ✅ | - | pypdf |
| Word (.docx) | ✅ | - | python-docx |
| PowerPoint (.pptx) | ✅ | - | python-pptx |
| Excel (.xlsx) | ✅ | - | openpyxl |

#### 电子书格式

| 格式 | 输入 | 输出 | 依赖包 |
|------|:----:|:----:|--------|
| EPUB (.epub) | ✅ | - | ebooklib |
| MOBI (.mobi) | ✅ | - | ebooklib |

#### 图像格式 (支持 OCR)

| 格式 | 输入 | 输出 | 依赖包 |
|------|:----:|:----:|--------|
| PNG (.png) | ✅ | - | Pillow |
| JPEG (.jpg/.jpeg) | ✅ | - | Pillow |
| GIF (.gif) | ✅ | - | Pillow |
| BMP (.bmp) | ✅ | - | Pillow |
| TIFF (.tiff) | ✅ | - | Pillow |
| WebP (.webp) | ✅ | - | Pillow |

#### 元数据提取

支持从 PDF、Word、Excel、EPUB 等格式提取元数据：
- 标题、作者、主题
- 创建/修改时间
- 关键词
- 页数、字数

### 3. 文档操作

- 加载/保存 Markdown 文件
- 选择器语法 (`doc.h1[0]`, `doc.p`, `doc.code`)
- 插入/删除/修改元素
- 批量操作

### 4. 文档分析

- 统计概览 (元素数量、字数、行数)
- 标题结构分析
- 链接/图片提取
- 关键词统计

### 5. 格式转换

- Markdown → HTML
- Markdown → 纯文本
- Markdown → JSON (AST 序列化)

### 6. 高级功能

#### 文档清理
- 移除页眉/页脚/页码
- 移除重复文本
- 修复编码问题
- 规范化空白字符
- 修复表格格式

#### 批量处理
- 多文件并行处理
- 多进程/多线程支持
- 批量格式转换
- 处理报告生成
- 失败重试机制

#### 结构化提取
- 标题/段落/链接提取
- 表格/代码块提取
- 邮箱/URL/日期提取
- 自定义 Schema 提取

#### 图片处理
- 图片提取与保存
- Base64 图片解码
- 远程图片下载

#### LLM 增强
- OpenAI 支持 (GPT-3.5/GPT-4)
- Anthropic 支持 (Claude)
- Ollama 本地模型支持
- 文本改进与 OCR 修复
- Markdown 格式优化
- 结构化数据提取

## 目录结构

```
mark/
├── ast_nodes.py        # AST 节点定义 (50+ 节点类型)
├── lexer.py            # 词法分析器 (Token 流生成)
├── parser.py           # 语法解析器 (AST 构建)
├── md_parser.py        # Markdown 解析引擎
├── md_generator.py     # Markdown 生成器
├── storage.py          # 存储引擎 (序列化/反序列化)
├── analyzer.py         # 分析引擎 (统计分析)
├── converter.py        # 格式转换器 (HTML/文本/JSON)
├── mdl_builtins.py     # 内置函数库
├── interpreter.py      # 解释器 (脚本执行)
├── formats.py          # 多格式支持 (PDF/DOCX/PPTX/XLSX/EPUB/MOBI)
├── cleaner.py          # 文档清理器
├── batch.py            # 批量处理器
├── extractor.py        # 结构化提取器
├── image_extractor.py  # 图片提取器
├── llm_enhancer.py     # LLM 增强器
├── cli.py              # 命令行工具
├── repl.py             # REPL 交互环境
├── mdl.py              # 主入口
├── examples/           # 示例文件
│   ├── demo.mdl        # MDL 脚本示例
│   └── example.md      # Markdown 示例
└── tests/              # 测试套件
    └── test_mdl.py     # 完整功能测试 (53 用例)
```

## 快速开始

### 环境要求

- Python 3.8+
- 无需额外依赖 (核心功能)
- 可选依赖: pypdf, python-docx, python-pptx, openpyxl, Pillow, pytesseract, ebooklib, pyyaml, toml, openai, anthropic

### 命令行使用

```bash
# 转换文档
python cli.py convert document.pdf output.md

# 批量处理
python cli.py batch "*.pdf" output/ --format md --workers 8

# 分析文档
python cli.py analyze document.md --verbose

# 清理文档
python cli.py clean document.md -o cleaned.md

# 提取结构化数据
python cli.py extract document.md --schema full -o data.json

# 提取图片
python cli.py images document.md --output images/

# 启动 REPL
python cli.py repl

# 运行脚本
python cli.py run script.mdl

# 显示系统信息
python cli.py info --formats
```

### 运行 REPL

```bash
python mdl.py
```

```
MDL REPL v1.0
输入 MDL 命令，输入 'exit' 退出
>>> load "example.md" as doc
>>> print doc.h1.count
>>> exit
```

### 运行脚本

```bash
python mdl.py script.mdl
```

### 运行测试

```bash
python tests/test_mdl.py
```

## MDL 语法示例

### 加载与保存

```mdl
load "document.md" as doc
save doc as "output.md"
```

### 选择器操作

```mdl
print doc.h1[0].text
print doc.p.count
print doc.code[0].language
```

### 修改文档

```mdl
set doc.h1[0].text = "新标题"
insert after doc.h1[0]: "这是新插入的段落"
remove doc.p[0]
```

### 循环与条件

```mdl
for heading in doc.h1:
    print heading.text
end

if doc.p.count > 0:
    print "文档包含段落"
end
```

### 格式转换

```mdl
convert doc to html save as "output.html"
convert doc to text save as "output.txt"
```

### 分析文档

```mdl
analyze doc
stats doc headings
stats doc links
```

### 新增命令

#### 格式转换

```mdl
transform "document.pdf" to "markdown"
transform "report.docx" to "markdown"
```

#### 文档清理

```mdl
clean doc
clean doc with remove_headers = true, remove_footers = true
```

#### 结构化提取

```mdl
extract doc schema "basic"
extract doc schema "full" output "data.json"
```

#### 批量处理

```mdl
batch ["*.md", "*.html"] output "converted/" format "markdown"
```

## 内置函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `upper(s)` | 转大写 | `upper("hello")` → `"HELLO"` |
| `lower(s)` | 转小写 | `lower("WORLD")` → `"world"` |
| `trim(s)` | 去除空白 | `trim("  hello  ")` → `"hello"` |
| `length(x)` | 获取长度 | `length([1,2,3])` → `3` |
| `contains(s, sub)` | 包含判断 | `contains("hello", "ell")` → `true` |
| `split(s, sep)` | 分割字符串 | `split("a,b,c", ",")` → `["a","b","c"]` |
| `join(list, sep)` | 连接字符串 | `join(["a","b"], "-")` → `"a-b"` |
| `replace(s, old, new)` | 替换字符串 | `replace("hello", "l", "L")` → `"heLLo"` |

## API 参考

### AST 节点类型

#### 文档结构节点
- `DocumentNode` - 文档根节点
- `HeadingNode` - 标题节点 (H1-H6)
- `ParagraphNode` - 段落节点

#### 文本格式节点
- `TextNode` - 纯文本节点
- `BoldNode` - 粗体节点
- `ItalicNode` - 斜体节点
- `BoldItalicNode` - 粗斜体节点
- `StrikethroughNode` - 删除线节点
- `SuperscriptNode` - 上标节点
- `SubscriptNode` - 下标节点
- `CodeInlineNode` - 行内代码节点
- `LineBreakNode` - 硬换行节点

#### 块级元素节点
- `CodeBlockNode` - 代码块节点
- `BlockquoteNode` - 引用块节点
- `HorizontalRuleNode` - 分隔线节点
- `HTMLBlockNode` - HTML 块节点

#### 列表节点
- `UnorderedListNode` - 无序列表
- `OrderedListNode` - 有序列表
- `TaskListNode` - 任务列表
- `ListItemNode` - 列表项
- `TaskItemNode` - 任务项

#### 表格节点
- `TableNode` - 表格
- `TableRowNode` - 表格行
- `TableCellNode` - 表格单元格

#### 链接与图片
- `LinkNode` - 链接节点
- `ImageNode` - 图片节点

#### 扩展语法节点
- `FootnoteRefNode` - 脚注引用
- `FootnoteDefNode` - 脚注定义
- `DefinitionListNode` - 定义列表
- `DefinitionItemNode` - 定义项
- `MathInlineNode` - 行内数学公式
- `MathBlockNode` - 块级数学公式

### Python API

```python
from md_parser import parse_markdown
from md_generator import generate_markdown
from analyzer import analyze
from converter import md_to_html, md_to_text
from formats import convert_to_markdown
from cleaner import clean_document
from extractor import extract_structured
from batch import batch_convert

# 解析 Markdown
doc = parse_markdown("# 标题\n\n段落内容")

# 转换为 HTML
html = md_to_html("# 标题")

# 分析文档
stats = analyze(doc)

# 多格式转换
md = convert_to_markdown("document.pdf")

# 清理文档
clean = clean_document(md)

# 结构化提取
data = extract_structured(md, "full")

# 批量处理
report = batch_convert(["*.md"], "output/", "html")
```

## 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    MDL 脚本                          │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              词法分析器 (Lexer)                      │
│         源码 → Token 流                              │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              语法解析器 (Parser)                     │
│         Token 流 → AST                              │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              解释器 (Interpreter)                    │
│         执行 AST 节点                                │
└─────────────────────┴───────────────────────────────┘
          │                    │
          ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│  Markdown 解析器  │  │   内置函数库      │
│  (md_parser)      │  │  (mdl_builtins)  │
└────────┬─────────┘  └──────────────────┘
         │
         ▼
┌──────────────────┐
│   AST 节点树      │
│  (ast_nodes)     │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│生成器  │ │分析器  │ │转换器  │ │清理器  │ │提取器  │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

## 更新日志

### v1.3.0 (2026-04-06)

#### 新增功能
- 图像格式支持 (PNG/JPEG/GIF/BMP/TIFF/WebP) + OCR
- LaTeX 格式支持
- Org-mode 格式支持
- MediaWiki/Wiki 格式支持
- XML 格式支持
- YAML 格式支持
- TOML 格式支持
- TSV 格式支持
- 文档元数据提取功能
- 格式分类系统
- 带元数据的转换功能
- 新增测试用例 11 个 (总计 53 个)

#### 改进
- 扩展格式注册表，支持 25+ 种格式
- 增强格式信息，添加类别字段
- 优化 MediaWiki 标题转换算法

### v1.2.0 (2026-04-06)

#### 新增功能
- EPUB/MOBI 电子书格式支持
- LLM 增强模式 (OpenAI/Anthropic/Ollama)
- 完整的命令行工具 (CLI)
- 多进程并行处理支持
- 批量处理失败重试机制
- 新增模块: `llm_enhancer.py`, `cli.py`
- 新增测试用例 3 个 (总计 42 个)

#### 改进
- 批量处理器支持多进程模式
- 批量处理报告增加吞吐量统计
- 支持进度回调函数

### v1.1.0 (2026-04-06)

#### 新增功能
- 多格式输入支持 (PDF/DOCX/PPTX/XLSX/HTML/CSV/RST/JSON)
- 文档清理功能 (页眉/页脚移除、编码修复、空白规范化)
- 批量处理功能 (多文件并行处理)
- 结构化提取功能 (标题/链接/表格/代码块提取)
- 图片提取功能 (Base64解码、远程下载)
- 新增 MDL 命令: `transform`, `clean`, `extract`, `batch`
- 新增 AST 节点类型: `MDLBatchNode`, `MDLCleanNode`, `MDLExtractNode`, `MDLTransformNode`
- 新增测试用例 4 个 (总计 39 个)

#### 改进
- 解释器支持新命令执行
- 词法分析器新增关键字
- 语法解析器新增语句解析

### v1.0.0 (2026-04-06)

#### 新增功能
- 完整的 MDL 语言实现 (词法分析、语法解析、解释器)
- 支持 20+ 种 Markdown 元素解析
- 新增上标/下标语法支持 (`^上标^`, `~下标~`)
- 新增脚注支持 (`[^id]` 引用和定义)
- 新增数学公式支持 (`$行内$`, `$$块级$$`)
- 新增定义列表支持
- REPL 交互环境
- 35 个测试用例全部通过

#### 核心模块
- `ast_nodes.py` - 45+ AST 节点类型
- `lexer.py` - 词法分析器
- `parser.py` - 语法解析器
- `md_parser.py` - Markdown 解析引擎
- `md_generator.py` - Markdown 生成器
- `converter.py` - 格式转换器
- `analyzer.py` - 分析引擎
- `storage.py` - 存储引擎
- `interpreter.py` - 解释器

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request
