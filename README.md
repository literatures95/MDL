# MDL - Universal Markdown Toolkit

MDL (Markdown Toolkit) 是一个**通用 Markdown 工具链和 LLM 数据操作台**。任意文档格式 → Markdown → 语义分块 → 向量存储 → RAG 检索，全流程覆盖。

```
PDF ─┐          ┌──────────┐       ┌──────────┐       ┌──────────┐
DOCX ─┤          │          │       │          │       │          │
HTML ─┼──► ANY ──┤   MD     ├──►   │  AST     ├──►   │ Vector   │
PPTX ─┤          │  Parser  │       │ Chunker  │       │ Store    │
EPUB ─┘          └──────────┘       └──────────┘       └────┬─────┘
                                                             │
                                                    ┌────────▼────────┐
                                                    │  RAG Query      │
                                                    │  (Search + LLM) │
                                                    └─────────────────┘
```


## 关键特色

- 🎯 **专一完整** - 专为 Markdown 操作优化，50+ AST 节点类型
- 📊 **功能丰富** - 支持 25+ 种文档格式互转，20+ Markdown 元素
- 🧠 **向量存储** - AST 语义分块 + 多后端 Embedding + 余弦相似度搜索
- 🤖 **RAG 管道** - 检索增强生成，支持 OpenAI/Anthropic/Ollama
- 🔄 **智能转换** - 任意格式 → Markdown → 任意格式
- 🌐 **网页抓取** - 支持 URL 内容抓取并转换为 Markdown
- 🧹 **文档优化** - 内置清洗、分析、提取、批量处理
- 📦 **生产就绪** - 10,000+ 行代码，53/53 测试通过


## 向量存储与 RAG

### 数据流向

```
文件 → formats.convert_to_markdown() → md_parser.parse() → DocumentNode(AST)
  → vector_chunker.chunk_document() → list[Chunk]（语义完整的分块）
  → embedding_provider.get_embeddings() → list[vector]
  → vector_store.add_chunks() → ~/.mdl/vector_store/
                                      │
查询 → embedding → vector_store.search() → RAGPipeline.query() → LLM 回答
```

### CLI 命令

```bash
# 索引文档（支持任意格式：PDF/DOCX/MD/HTML……）
mdl vector index document.pdf --collection mydocs

# 索引整个目录
mdl vector index ./docs/ --collection project

# 使用本地 Ollama 嵌入（无需 API Key）
mdl vector index README.md --collection test --embedding ollama

# 语义搜索
mdl vector search "Markdown 表格如何解析" --collection mydocs

# RAG 问答
mdl query "项目支持哪些格式转换？" --collection mydocs --provider ollama
mdl query "这是什么项目？" --collection mydocs --provider openai

# 管理向量集合
mdl vector list
mdl vector info mydocs
mdl vector delete mydocs
```

### 语义分块策略

区别于简单的按 token 数切块，MDL 利用现有 AST 解析能力做**语义级分块**：

| 策略 | 通用做法 | MDL 做法 |
|------|---------|----------|
| 分块边界 | 固定 token 数 | **按标题层级**（H1 > H2 > H3） |
| 语义完整性 | 可能切断段落/表格 | **在段落边界切割**，保留完整元素 |
| 层级信息 | 丢失 | **保留 heading_path**（如 "安装 > 配置 > 环境变量"） |
| 块间重叠 | 字符级 | **段落级**，保证语义完整 |
| 元数据 | 无 | 记录 source_path、heading_path、行号范围 |

### 多后端 Embedding

| 提供者 | 默认模型 | 是否需要 API Key | 说明 |
|--------|---------|:----------------:|------|
| OpenAI | text-embedding-3-small | ✅ | 云端，高精度 |
| Ollama | nomic-embed-text | ❌ | 本地运行，免费 |
| sentence-transformers | all-MiniLM-L6-v2 | ❌ | 本地，需安装包 |
| fallback | — | ❌ | 哈希嵌入，离线测试用 |

### MDL 脚本中的向量操作

```mdl
// 索引文档
vector_index("README.md", "my_collection", 1000, 200, "fallback")

// 搜索
results = vector_search("Markdown 解析", "my_collection", 5, "fallback")
print results[0].text
print results[0].score
```

### Python API

```python
from vector_chunker import MarkdownChunker, ChunkerConfig
from vector_embeddings import create_embedding_provider
from vector_store import VectorStore
from vector_rag import RAGPipeline

# 语义分块
chunker = MarkdownChunker(ChunkerConfig(chunk_size=1000))
chunks = chunker.chunk_file("document.md")

# 嵌入 + 存储
embedder = create_embedding_provider("ollama")
store = VectorStore()
embeddings = embedder.get_embeddings([c.text for c in chunks])
store.add_chunks("docs", chunks, embeddings)

# RAG 查询
pipeline = RAGPipeline(vector_store=store, embedding_provider=embedder)
result = pipeline.query("项目是做什么的？", collection_name="docs")
print(result["answer"])
```


## 多格式支持

### 文档格式互转

| 格式 | 输入 | 输出 | 依赖 |
|------|:----:|:----:|------|
| Markdown (.md) | ✅ | ✅ | 内置 |
| HTML (.html) | ✅ | ✅ | 内置 |
| 纯文本 (.txt) | ✅ | ✅ | 内置 |
| PDF (.pdf) | ✅ | ✅ | pypdf / pdfplumber + Pandoc/ConTeXt |
| Word (.docx) | ✅ | ✅ | python-docx |
| PowerPoint (.pptx) | ✅ | - | python-pptx |
| Excel (.xlsx) | ✅ | - | openpyxl |
| EPUB (.epub) | ✅ | - | ebooklib |
| MOBI (.mobi) | ✅ | - | ebooklib |
| LaTeX (.tex) | ✅ | ✅ | 内置 |
| reStructuredText (.rst) | ✅ | ✅ | 内置 |
| Org-mode (.org) | ✅ | ✅ | 内置 |
| MediaWiki (.wiki) | ✅ | ✅ | 内置 |
| CSV / TSV | ✅ | ✅ | 内置 |
| JSON | ✅ | ✅ | 内置 |
| XML | ✅ | ✅ | 内置 |
| YAML | ✅ | ✅ | pyyaml |
| TOML | ✅ | ✅ | toml |
| 图片 (PNG/JPEG/GIF/BMP/TIFF/WebP) | ✅ | - | Pillow (+ OCR: pytesseract) |
| URL / 网页 | ✅ | - | requests + beautifulsoup4 |

```bash
# 任意格式 → Markdown
mdl convert document.pdf output.md
mdl convert report.docx output.md

# Markdown → 任意格式
mdl convert document.md output.html
mdl convert document.md output.pdf --template technical

# 批量转换
mdl batch "*.pdf" output/ --format md --workers 8
```

### 元数据提取

支持从 PDF、Word、Excel、EPUB 等格式提取：标题、作者、主题、关键词、创建/修改时间、页数、字数。


## 文档分析

```bash
# 完整分析报告
mdl analyze document.md --verbose

# 结构化数据提取
mdl extract document.md --schema full -o data.json

# 文档清洗
mdl clean document.md -o cleaned.md --headers --footers

# 图片提取
mdl images document.md --output images/

# 语义搜索（向量检索）
mdl vector search "性能优化建议" --collection mydocs
```

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

# 多格式转换
md = convert_to_markdown("document.pdf")

# 文档分析
stats = analyze(doc)

# 批量处理
report = batch_convert(["*.md"], "output/", "html")
```


## MDL 脚本语言

MDL 内置领域特定语言，支持文档操作的脚本化：

```mdl
// 加载与操作
load "document.md" as doc
set doc.h1[0].text = "新标题"
insert after doc.h1[0]: "新段落"

// 循环与条件
for h in select(doc, "heading"):
    print h.text
end

// 转换与分析
convert doc to html save as "output.html"
analyze doc

// 向量操作
vector_index("document.md", "docs")
vector_query("这个文档讲了什么？", "docs", 5, "ollama")
```

### 启动方式

```bash
python cli.py repl       # REPL 交互环境
python cli.py run script.mdl   # 运行脚本文件
python mdl.py             # 快速进入 REPL
```


## 项目统计

| 指标 | 数据 |
|------|------|
| Python 文件 | 25 个 |
| 总代码行数 | 10,000+ 行 |
| 测试用例 | 53 个 |
| AST 节点类型 | 50+ 种 |
| 支持 Markdown 元素 | 20+ 种 |
| 支持输入格式 | 25+ 种 |
| Embedding 提供者 | 4 种 |
| LLM 提供者 | 3 种 |

## 目录结构

```
├── core/                  # 核心引擎
│   ├── ast_nodes.py       # AST 节点定义 (50+ 节点类型)
│   ├── lexer.py           # 词法分析器
│   ├── parser.py          # 语法解析器
│   ├── interpreter.py     # 解释器
│   └── mdl_builtins.py    # 内置函数库
├── markdown/              # Markdown 处理
│   ├── md_parser.py       # Markdown 解析引擎
│   └── md_generator.py    # Markdown 生成器
├── convert/               # 格式转换
│   ├── converter.py       # 格式转换器 (HTML/文本/JSON)
│   ├── formats.py         # 多格式支持 (25+ 格式)
│   └── format_conversion_enhanced.py  # 增强转换
├── vector/                # 向量存储与检索  ← 新增
│   ├── vector_chunker.py      # AST 语义分块器
│   ├── vector_embeddings.py   # Embedding 提供者
│   ├── vector_store.py        # 向量存储引擎
│   └── vector_rag.py          # RAG 查询管道
├── analyze/               # 分析与提取
│   ├── analyzer.py        # 分析引擎
│   ├── extractor.py       # 结构化提取器
│   └── cleaner.py         # 文档清理器
├── io/                    # 输入输出
│   ├── storage.py         # 存储引擎
│   ├── image_extractor.py # 图片提取器
│   └── batch.py           # 批量处理器
├── enhance/               # LLM 增强
│   └── llm_enhancer.py    # LLM 增强器
├── cli/                   # 命令行
│   ├── cli.py             # 命令行工具
│   ├── repl.py            # REPL 交互环境
│   └── mdl.py             # 主入口
├── build.py               # PDF 构建脚本
├── Makefile               # 自动化构建
├── templates/             # ConTeXt 模板
├── examples/              # 示例文件
└── tests/                 # 测试套件
    └── test_mdl.py        # 53 个测试用例
```

注：当前文件位于根目录（尚未重组为子目录结构），上述为规划中的目标结构。


## 更新日志

### v1.5.0 (2026-04-24)

#### 新增功能
- **向量存储引擎** (`vector_store.py`) - 文件式持久化向量库，纯 Python 余弦相似度搜索
- **语义分块器** (`vector_chunker.py`) - 基于 AST 的 Markdown 语义分块，按标题层级 + 段落边界切割
- **多后端 Embedding** (`vector_embeddings.py`) - 支持 OpenAI、Ollama、sentence-transformers、fallback
- **RAG 查询管道** (`vector_rag.py`) - 检索增强生成，自动格式化上下文 + LLM 回答
- CLI 新增 `vector` 和 `query` 子命令组
- MDL 语言新增 `vector_index`、`vector_search`、`vector_query` 内建函数

### v1.4.0 (2026-04-06)

- 专业 PDF 排版 (ConTeXt + Pandoc)
- 自定义模板系统

### v1.3.0 (2026-04-06)

- 图像格式支持 + OCR
- LaTeX/Org-mode/MediaWiki/XML/YAML/TOML 格式

### v1.2.0 (2026-04-06)

- EPUB/MOBI 电子书支持
- LLM 增强 (OpenAI/Anthropic/Ollama)
- CLI 工具、多进程批量处理

### v1.1.0 (2026-04-06)

- 多格式输入 (PDF/DOCX/PPTX/XLSX/HTML/CSV/RST/JSON)
- 文档清洗、批量处理、结构化提取、图片处理

### v1.0.0 (2026-04-06)

- 完整的 MDL 语言实现（词法/语法/解释器）
- Markdown 解析引擎（20+ 元素）
- REPL 交互环境


## 环境要求与安装

- Python 3.8+
- 核心功能零依赖
- 可选依赖：`pip install pypdf pdfplumber python-docx python-pptx openpyxl Pillow pytesseract ebooklib pyyaml toml requests beautifulsoup4 openai anthropic sentence-transformers`
- PDF 排版：需要安装 Pandoc + ConTeXt

```bash
# 运行测试
python tests/test_mdl.py

# 检查 lint
python -m ruff check .
```

## 相关资源

- [语言分析.md](语言分析.md) - 语言设计文档
- [examples/demo.mdl](examples/demo.mdl) - 脚本示例
- [examples/example.md](examples/example.md) - Markdown 示例
- [tests/test_mdl.py](tests/test_mdl.py) - 测试套件

## 许可证

MIT License
