# MDL - Markdown 操作语言

MDL (Markdown Operation Language) 是一个专门为 Markdown 文档操作设计的领域特定语言 (DSL)，提供完美的 Markdown 解析、修改、转换和分析功能。


## 关键特色

- 🎯 **专一完整** - 专为 Markdown 操作优化，50+ AST 节点类型
- 📊 **功能丰富** - 支持 20+ Markdown 元素，25+ 种文件格式转换
- 🔄 **智能转换** - 支持 HTML、PDF、JSON、LaTeX 等 15+ 种输出格式
- 🤖 **AI 赋能** - 集成 OpenAI/Anthropic/Ollama LLM 能力
- 🧹 **文档优化** - 内置清理、分析、提取、优化等高级功能
- 📦 **生产就绪** - 9000+ 行代码，53/53 测试通过，100% 完成度

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
| Python 文件 | 21 个 |
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
| PDF (.pdf) | ✅ | ✅ | pandoc + context |
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

#### 专业排版 (基于 ConTeXt)
- **高质量 PDF 生成** - 使用 Pandoc + ConTeXt 引擎
- **内容与表现分离** - 自定义模板系统
- **专业文档模板** - 默认、技术文档、书籍模板
- **排版参数控制** - 纸张大小、字体、页边距
- **自动构建系统** - Makefile 和 Python 构建脚本
- **文件监听模式** - 自动重新构建

```bash
# 使用默认模板生成 PDF
mdl convert document.md output.pdf

# 使用技术文档模板
mdl convert document.md output.pdf --template technical

# 高级排版控制
mdl convert document.md output.pdf \
  --paper-size letter \
  --font-size 12 \
  --margins 1in

# 使用构建脚本
python build.py document.md --watch
make build INPUT=document.md
```

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
├── build.py            # PDF 构建脚本
├── Makefile            # 自动化构建系统
├── templates/          # ConTeXt 模板目录
│   ├── default.ctx     # 默认文档模板
│   └── technical.ctx   # 技术文档模板
├── examples/           # 示例文件
│   ├── demo.mdl        # MDL 脚本示例
│   └── example.md      # Markdown 示例
└── tests/              # 测试套件
    └── test_mdl.py     # 完整功能测试 (53 用例)
```

## MDL 语言概览

MDL 是一个**完全成熟的编程语言**，具有完整的编译-执行流程：

```
源代码 (.mdl) → 词法分析 → 语法解析 → AST → 解释执行 → 结果
```

### 核心语言特性

| 特性 | 描述 | 示例 |
|------|------|------|
| **数据类型** | 字符串、数字、布尔、数组、字典等 | `name = "MDL"`, `count = 42` |
| **控制流** | if/elif/else, for 循环，函数定义 | `if x > 0: ... end` |
| **文档操作** | load, save, set, insert, append, remove | `load "file.md" as doc` |
| **选择器** | 类似 CSS 的元素选择 | `doc.h1[0]`, `doc.p`, `select(doc, "code")` |
| **变换** | convert, transform, analyze, clean, extract | `convert doc to html` |
| **表达式** | 算术、比较、逻辑、字符串操作 | `a + b`, `len(list)`, `text.upper()` |

### 语言示例

```mdl
// 加载文档
load "document.md" as doc

// 遍历标题
for h in select(doc, "heading"):
    print h.text
end

// 修改内容
set doc.h1[0].text = "新标题"

// 格式转换
convert doc to html save as "output.html"

// 保存
save doc as "modified.md"
```

## 快速开始

### 环境要求

- Python 3.8+
- 无需额外依赖 (核心功能)
- 可选依赖: pypdf, python-docx, python-pptx, openpyxl, Pillow, pytesseract, ebooklib, pyyaml, toml, openai, anthropic
- **PDF 排版**: Pandoc + ConTeXt (推荐用于高质量 PDF 输出)

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

# 生成高质量 PDF (需要 Pandoc + ConTeXt)
python cli.py convert document.md output.pdf --template technical

# 使用构建脚本
python build.py document.md --watch
make build INPUT=document.md

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

MDL 采用经典的**编译原理三层架构**：

```
┌──────────────────────────────────────────────────────────┐
│                   MDL 脚本文件 (.mdl)                     │
└─────────────────────────┬────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────┐
│              第一层: 词法分析 (Lexer)                     │
│         将源代码转换成 Token 流                            │
│         模块: lexer.py (Token 生成)                      │
└─────────────────────────┬────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────┐
│              第二层: 语法分析 (Parser)                    │
│         将 Token 流转换成抽象语法树 (AST)                  │
│         模块: parser.py (递归下降解析)                    │
└─────────────────────────┬────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────┐
│              第三层: 执行引擎 (Interpreter)               │
│         遍历并执行 AST 节点                                │
│         模块: interpreter.py (树遍历解释器)              │
└────────┬──────────────────────────┬──────────────────────┘
         │                          │
    ┌────▼────┬──────────┬─────────▼┐
    ▼         ▼          ▼          ▼
   AST 节点系统 (ast_nodes.py, 50+ 种节点)
    │         │          │
    ├─────────┼──────────┼─────────────────┼────────────┐
    │         │          │                 │            │
    ▼         ▼          ▼                 ▼            ▼
Markdown    存储引擎   分析引擎          高级功能    LLM 集成
解析/生成   (storage) (analyzer)       (batch/     (llm_
(md_parser/ (文件序列  (统计分析)       clean/      enhancer)
 md_gen)    化)                       extract)
```

### 核心模块

| 模块 | 功能 | 行数 |
|------|------|------|
| `lexer.py` | 词法分析 - Token 生成 | ~200 |
| `parser.py` | 语法分析 - AST 构建 | ~500 |
| `interpreter.py` | 执行引擎 - 节点执行 | ~400 |
| `ast_nodes.py` | AST 节点定义 - 50+ 种节点 | ~300 |
| `md_parser.py` | Markdown 解析 - 20+ 元素 | ~600 |
| `md_generator.py` | Markdown 生成 - 反向转换 | ~400 |
| `storage.py` | 存储引擎 - 文件 I/O | ~300 |
| `analyzer.py` | 分析引擎 - 统计/可读性 | ~400 |
| `converter.py` | 格式转换 - HTML/文本/JSON | ~300 |
| `mdl_builtins.py` | 内置函数库 - 核心函数 | ~400 |
| `formats.py` | 多格式支持 - 25+ 格式 | ~800 |
| `cleaner.py` | 文档清理 - 规范化/修复 | ~300 |
| `batch.py` | 批量处理 - 并行化 | ~300 |
| `extractor.py` | 结构化提取 - 数据萃取 | ~250 |
| `image_extractor.py` | 图像处理 - 提取/下载/OCR | ~250 |
| `llm_enhancer.py` | LLM 增强 - AI 能力 | ~350 |
| `cli.py` | 命令行工具 - CLI 界面 | ~500 |
| `repl.py` | REPL 环境 - 交互式 Shell | ~200 |
| `build.py` | PDF 构建脚本 - 专业排版 | ~200 |
| `Makefile` | 自动化构建 - 工作流管理 | ~50 |

**总计**: 9,200+ 行生产级代码

## 更新日志

### v1.4.0 (2026-04-06)

#### 新增功能
- 专业 PDF 排版支持 (基于 ConTeXt + Pandoc)
- 自定义模板系统 (默认、技术文档模板)
- 高级排版参数控制 (纸张大小、字体、页边距)
- 自动化构建脚本 (`build.py`, `Makefile`)
- 文件监听模式 (自动重新构建)
- 新增模块: `build.py`, `Makefile`, `templates/`
- 新增 ConTeXt 模板文件: `default.ctx`, `technical.ctx`

#### 改进
- CLI 支持 PDF 输出格式
- 扩展格式转换选项
- 增强构建工作流

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

## 官方文档

- **[语言分析.md](语言分析.md)** - MDL 深度分析（推荐阅读）
  - 完整的语言设计文档
  - 所有语法规范和示例
  - 核心函数库参考
  - 应用场景和最佳实践
  - 架构设计详解

- **[README.md](README.md)** - 快速入门指南（本文件）
  - 功能概览
  - 命令行使用
  - API 参考

## 相关资源

- MDL 脚本示例: [examples/demo.mdl](examples/demo.mdl)
- Markdown 测试文件: [examples/example.md](examples/example.md)
- 完整测试套件: [tests/test_mdl.py](tests/test_mdl.py)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request
