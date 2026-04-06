# MDL 构建系统 - 基于 ConTeXt 的专业排版
# 参考: https://dave.autonoma.ca/blog/2019/05/22/typesetting-markdown-part-1/

.PHONY: help clean build watch install-deps check-deps

# 默认目标
help:
	@echo "MDL 构建系统 - 专业 Markdown 到 PDF 转换"
	@echo ""
	@echo "可用目标:"
	@echo "  build        - 构建所有文档"
	@echo "  clean        - 清理构建产物"
	@echo "  watch        - 监听文件变化并重新构建"
	@echo "  install-deps - 安装依赖 (Pandoc, ConTeXt)"
	@echo "  check-deps   - 检查依赖是否已安装"
	@echo ""
	@echo "使用示例:"
	@echo "  make build INPUT=document.md"
	@echo "  make build INPUT=document.md TEMPLATE=technical"
	@echo "  make watch INPUT=document.md"

# 变量
INPUT ?= README.md
OUTPUT ?= $(basename $(INPUT)).pdf
TEMPLATE ?= default
PAPER_SIZE ?= a4
FONT_SIZE ?= 11
MARGINS ?= 2.5cm

# 构建 PDF
build:
	@echo "构建 $(INPUT) -> $(OUTPUT)"
	python build.py $(INPUT) \
		-o $(OUTPUT) \
		-t $(TEMPLATE) \
		--paper-size $(PAPER_SIZE) \
		--font-size $(FONT_SIZE) \
		--margins $(MARGINS)

# 监听模式
watch:
	@echo "监听 $(INPUT) 的变化..."
	python build.py $(INPUT) \
		-t $(TEMPLATE) \
		--paper-size $(PAPER_SIZE) \
		--font-size $(FONT_SIZE) \
		--margins $(MARGINS) \
		--watch

# 清理构建产物
clean:
	@echo "清理构建产物..."
	find . -name "*.pdf" -type f -delete
	find . -name "*.tuc" -type f -delete
	find . -name "*.log" -type f -delete
	find . -name "*.tmp" -type f -delete

# 检查依赖
check-deps:
	@echo "检查依赖..."
	@command -v pandoc >/dev/null 2>&1 && echo "✓ Pandoc 已安装" || echo "✗ Pandoc 未安装"
	@command -v context >/dev/null 2>&1 && echo "✓ ConTeXt 已安装" || echo "✗ ConTeXt 未安装"
	@python --version >/dev/null 2>&1 && echo "✓ Python 已安装" || echo "✗ Python 未安装"

# 安装依赖 (Linux)
install-deps:
	@echo "安装依赖..."
	@echo "请根据您的系统安装以下软件:"
	@echo "  - Pandoc: https://pandoc.org/installing.html"
	@echo "  - ConTeXt: https://wiki.contextgarden.net/Installation"
	@echo ""
	@echo "Ubuntu/Debian:"
	@echo "  sudo apt update"
	@echo "  sudo apt install pandoc context"
	@echo ""
	@echo "macOS (使用 Homebrew):"
	@echo "  brew install pandoc"
	@echo "  brew install context"
	@echo ""
	@echo "Windows:"
	@echo "  - 下载 Pandoc: https://github.com/jgm/pandoc/releases"
	@echo "  - 下载 ConTeXt: https://wiki.contextgarden.net/Installation"

# 构建示例文档
examples:
	@echo "构建示例文档..."
	make build INPUT=examples/demo.md OUTPUT=examples/demo.pdf
	make build INPUT=examples/example.md OUTPUT=examples/example.pdf TEMPLATE=technical

# 构建所有文档
all: examples
	@echo "构建所有文档完成"