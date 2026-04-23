"""MDL Embedding 提供者 - 多后端向量嵌入生成"""

import os
import hashlib
from dataclasses import dataclass


@dataclass
class EmbeddingConfig:
    """嵌入配置"""
    provider: str = "openai"
    model: str = ""
    api_key: str = ""
    api_base: str = ""


class EmbeddingProvider:
    """嵌入提供者基类"""

    def __init__(self, config: EmbeddingConfig):
        self.config = config

    def is_available(self) -> bool:
        return False

    def get_embedding(self, text: str) -> list[float]:
        raise NotImplementedError

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [self.get_embedding(t) for t in texts]

    @property
    def dimension(self) -> int:
        return 0


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI 嵌入提供者"""

    DEFAULT_MODEL = "text-embedding-3-small"

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        if not config.model:
            config.model = self.DEFAULT_MODEL
        self._dim = 1536 if "small" in config.model else 3072

    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401
            return bool(os.environ.get("OPENAI_API_KEY") or self.config.api_key)
        except ImportError:
            return False

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.config.api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=self.config.api_base or None,
            )
            # 分批处理，每批 20 条
            batch_size = 20
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = client.embeddings.create(model=self.config.model, input=batch)
                batch_emb = [d.embedding for d in response.data]
                all_embeddings.extend(batch_emb)
            return all_embeddings
        except Exception as e:
            print(f"[MDL] OpenAI embedding 失败: {e}")
            return []

    def get_embedding(self, text: str) -> list[float]:
        result = self.get_embeddings([text])
        return result[0] if result else []

    @property
    def dimension(self) -> int:
        return self._dim


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama 本地嵌入提供者"""

    DEFAULT_MODEL = "nomic-embed-text"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        if not config.model:
            config.model = self.DEFAULT_MODEL
        self.base_url = config.api_base or self.DEFAULT_BASE_URL
        self._dim = 768

    def is_available(self) -> bool:
        try:
            import requests
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_embedding(self, text: str) -> list[float]:
        try:
            import requests
            r = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.config.model, "prompt": text},
                timeout=30,
            )
            if r.status_code == 200:
                return r.json().get("embedding", [])
            else:
                print(f"[MDL] Ollama embedding 错误: {r.status_code}")
                return []
        except Exception as e:
            print(f"[MDL] Ollama embedding 失败: {e}")
            return []

    @property
    def dimension(self) -> int:
        return self._dim


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """本地 sentence-transformers 嵌入提供者"""

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        if not config.model:
            config.model = self.DEFAULT_MODEL
        self._model = None

    def is_available(self) -> bool:
        try:
            import sentence_transformers  # noqa: F401
            return True
        except ImportError:
            return False

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.config.model)
            except Exception as e:
                print(f"[MDL] 加载模型失败: {e}")
                raise

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            self._load_model()
            embeddings = self._model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            print(f"[MDL] sentence-transformers embedding 失败: {e}")
            return []

    def get_embedding(self, text: str) -> list[float]:
        result = self.get_embeddings([text])
        return result[0] if result else []

    @property
    def dimension(self) -> int:
        return 384  # all-MiniLM-L6-v2


class FallbackEmbeddingProvider(EmbeddingProvider):
    """基于哈希的 fallback 嵌入（仅用于测试/离线场景）"""

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self._dim = 64

    def is_available(self) -> bool:
        return True

    def get_embedding(self, text: str) -> list[float]:
        h = hashlib.md5(text.encode("utf-8"))
        digest = h.digest()
        vec = [float(b) / 255.0 for b in digest]
        # 扩展到 64 维
        vec = vec * 4
        vec = vec[:64]
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @property
    def dimension(self) -> int:
        return self._dim


PROVIDERS = {
    "openai": OpenAIEmbeddingProvider,
    "ollama": OllamaEmbeddingProvider,
    "sentence-transformers": SentenceTransformerEmbeddingProvider,
    "fallback": FallbackEmbeddingProvider,
}


def create_embedding_provider(
    provider_name: str = "openai",
    model: str = "",
    api_key: str = "",
    api_base: str = "",
) -> EmbeddingProvider:
    """创建嵌入提供者的工厂函数"""
    config = EmbeddingConfig(
        provider=provider_name,
        model=model,
        api_key=api_key,
        api_base=api_base,
    )
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"不支持的嵌入提供者: {provider_name}，可选: {', '.join(PROVIDERS)}")
    return cls(config)
