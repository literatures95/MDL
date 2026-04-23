"""MDL LLM 增强模块 - 使用 LLM 提高文档处理准确性"""

import os
import re
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    api_base: str = ""
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: int = 60


@dataclass
class EnhancementResult:
    """增强结果"""
    original: str
    enhanced: str
    improvements: List[str] = field(default_factory=list)
    confidence: float = 0.0


class LLMProvider:
    """LLM 提供者基类"""

    def __init__(self, config: LLMConfig):
        self.config = config

    def is_available(self) -> bool:
        """检查是否可用"""
        return False

    def complete(self, prompt: str) -> Optional[str]:
        """完成提示"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI 提供者"""

    def is_available(self) -> bool:
        """检查是否可用"""
        try:
            import openai  # noqa: F401
            return True
        except ImportError:
            return False

    def complete(self, prompt: str) -> Optional[str]:
        """完成提示"""
        if not self.is_available():
            return None
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.config.api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=self.config.api_base or None,
            )
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM] OpenAI 调用失败: {e}")
            return None


class AnthropicProvider(LLMProvider):
    """Anthropic 提供者"""

    def is_available(self) -> bool:
        """检查是否可用"""
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False

    def complete(self, prompt: str) -> Optional[str]:
        """完成提示"""
        if not self.is_available():
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(
                api_key=self.config.api_key or os.environ.get("ANTHROPIC_API_KEY"),
            )
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"[LLM] Anthropic 调用失败: {e}")
            return None


class OllamaProvider(LLMProvider):
    """Ollama 本地模型提供者"""

    def is_available(self) -> bool:
        """检查是否可用"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def complete(self, prompt: str) -> Optional[str]:
        """完成提示"""
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.config.timeout,
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            print(f"[LLM] Ollama 调用失败: {e}")
        return None


class LLMEnhancer:
    """LLM 增强器"""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.provider = self._get_provider()

    def _get_provider(self) -> Optional[LLMProvider]:
        """获取提供者"""
        provider_class = self.PROVIDERS.get(self.config.provider)
        if provider_class:
            provider = provider_class(self.config)
            if provider.is_available():
                return provider
        return None

    def is_available(self) -> bool:
        """检查是否可用"""
        return self.provider is not None

    def enhance_text(self, text: str, task: str = "improve") -> EnhancementResult:
        """增强文本"""
        if not self.provider:
            return EnhancementResult(original=text, enhanced=text)

        prompts = {
            "improve": f"""请改进以下文本的格式和可读性，保持原意不变：

{text}

请直接输出改进后的文本，不要添加任何解释。""",
            "fix_ocr": f"""以下文本是从 OCR 识别得到的，可能包含错误。请修复明显的识别错误：

{text}

请直接输出修复后的文本，不要添加任何解释。""",
            "summarize": f"""请总结以下文本的主要内容：

{text}

请用简洁的语言总结，不要添加任何解释。""",
            "translate": f"""请将以下文本翻译成中文：

{text}

请直接输出翻译结果，不要添加任何解释。""",
            "extract_structure": f"""请从以下文本中提取结构化信息，以 JSON 格式输出：

{text}

请输出 JSON 格式的结构化数据。""",
        }

        prompt = prompts.get(task, prompts["improve"])
        enhanced = self.provider.complete(prompt)

        if enhanced:
            improvements = self._detect_improvements(text, enhanced)
            return EnhancementResult(
                original=text,
                enhanced=enhanced.strip(),
                improvements=improvements,
                confidence=0.8,
            )
        return EnhancementResult(original=text, enhanced=text)

    def _detect_improvements(self, original: str, enhanced: str) -> List[str]:
        """检测改进点"""
        improvements = []
        if len(enhanced) > len(original) * 1.1:
            improvements.append("内容扩充")
        elif len(enhanced) < len(original) * 0.9:
            improvements.append("内容精简")
        if enhanced.count("\n") > original.count("\n"):
            improvements.append("格式优化")
        if re.search(r"[。，、；：？！]", enhanced) and not re.search(r"[。，、；：？！]", original):
            improvements.append("标点修复")
        return improvements

    def enhance_markdown(self, markdown: str) -> EnhancementResult:
        """增强 Markdown 文档"""
        if not self.provider:
            return EnhancementResult(original=markdown, enhanced=markdown)

        prompt = f"""请改进以下 Markdown 文档的格式和结构，确保：
1. 标题层级正确
2. 列表格式规范
3. 代码块标记正确
4. 表格格式完整
5. 链接和图片语法正确

原文档：
{markdown}

请直接输出改进后的 Markdown 文档，不要添加任何解释。"""

        enhanced = self.provider.complete(prompt)

        if enhanced:
            improvements = self._detect_improvements(markdown, enhanced)
            return EnhancementResult(
                original=markdown,
                enhanced=enhanced.strip(),
                improvements=improvements,
                confidence=0.85,
            )
        return EnhancementResult(original=markdown, enhanced=markdown)

    def extract_with_schema(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Schema 提取结构化数据"""
        if not self.provider:
            return {}

        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
        prompt = f"""请从以下文本中提取结构化信息。

文本：
{text}

提取 Schema：
{schema_str}

请按照 Schema 格式输出 JSON 数据，不要添加任何解释。"""

        result = self.provider.complete(prompt)

        if result:
            try:
                json_match = re.search(r"\{[\s\S]*\}", result)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {}

    def fix_table(self, table_md: str) -> str:
        """修复表格格式"""
        if not self.provider:
            return table_md

        prompt = f"""请修复以下 Markdown 表格的格式问题：

{table_md}

要求：
1. 确保所有行的列数一致
2. 添加正确的分隔行
3. 对齐表格内容

请直接输出修复后的表格，不要添加任何解释。"""

        result = self.provider.complete(prompt)
        return result.strip() if result else table_md

    def improve_chinese(self, text: str) -> str:
        """改进中文文本"""
        if not self.provider:
            return text

        prompt = f"""请改进以下中文文本：

{text}

要求：
1. 修复错别字
2. 改进语句通顺度
3. 规范标点符号
4. 保持原意不变

请直接输出改进后的文本，不要添加任何解释。"""

        result = self.provider.complete(prompt)
        return result.strip() if result else text


def enhance_with_llm(
    content: str,
    task: str = "improve",
    provider: str = "openai",
    model: str = "gpt-3.5-turbo",
    api_key: str = "",
) -> EnhancementResult:
    """使用 LLM 增强内容的便捷函数"""
    config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
    )
    enhancer = LLMEnhancer(config)
    if task == "markdown":
        return enhancer.enhance_markdown(content)
    return enhancer.enhance_text(content, task)


def extract_structured_with_llm(
    text: str,
    schema: Dict[str, Any],
    provider: str = "openai",
    model: str = "gpt-3.5-turbo",
) -> Dict[str, Any]:
    """使用 LLM 提取结构化数据的便捷函数"""
    config = LLMConfig(provider=provider, model=model)
    enhancer = LLMEnhancer(config)
    return enhancer.extract_with_schema(text, schema)
