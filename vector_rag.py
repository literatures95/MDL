"""MDL RAG 管道 - 检索增强生成"""

from typing import Optional

from vector_store import VectorStore, SearchResult
from vector_embeddings import (
    EmbeddingProvider,
)
from llm_enhancer import LLMEnhancer, LLMConfig


DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant answering questions based on the provided context.

Follow these rules:
1. Answer concisely and accurately using ONLY the information in the context below.
2. If the context does not contain enough information, say "根据提供的上下文，我无法回答这个问题" (in Chinese) or "I cannot answer this question based on the available context."
3. Use the same language as the question to answer.
4. Always cite the source (heading path) when referencing specific information.
5. Do not make up or fabricate information.

Context:
{context}

Question: {question}
Answer:"""


class RAGPipeline:
    """检索增强生成管道"""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
        llm_enhancer: Optional[LLMEnhancer] = None,
        llm_config: Optional[LLMConfig] = None,
    ):
        self.store = vector_store
        self.embedder = embedding_provider
        if llm_enhancer:
            self.llm = llm_enhancer
        elif llm_config:
            self.llm = LLMEnhancer(llm_config)
        else:
            self.llm = None

    @property
    def is_available(self) -> bool:
        """检查管道是否可用"""
        return self.embedder.is_available() and (
            self.llm is None or self.llm.is_available()
        )

    def query(
        self,
        question: str,
        collection_name: str = "default",
        top_k: int = 5,
        system_prompt: str = "",
    ) -> dict:
        """执行 RAG 查询

        返回:
            {"answer": str, "sources": list[dict], "chunks": list[dict], "error": str}
        """
        # 1. 嵌入问题
        query_vector = self.embedder.get_embedding(question)
        if not query_vector:
            return {
                "answer": "",
                "sources": [],
                "chunks": [],
                "error": "嵌入查询失败，请检查 embedding 提供者配置",
            }

        # 2. 向量搜索
        try:
            results = self.store.search(collection_name, query_vector, top_k=top_k)
        except Exception as e:
            return {
                "answer": "",
                "sources": [],
                "chunks": [],
                "error": f"搜索失败: {e}",
            }

        if not results:
            return {
                "answer": "未找到相关上下文",
                "sources": [],
                "chunks": [],
                "error": "",
            }

        # 3. 格式化上下文
        context = self._format_context(results)

        # 4. 如果有 LLM，调用生成回答
        if self.llm and self.llm.is_available():
            prompt_template = system_prompt or DEFAULT_SYSTEM_PROMPT
            prompt = prompt_template.format(
                context=context,
                question=question,
            )
            try:
                answer = self.llm.provider.complete(prompt)
            except Exception as e:
                answer = ""
                return {
                    "answer": f"LLM 调用失败: {e}",
                    "sources": self._format_sources(results),
                    "chunks": self._format_chunks(results),
                    "error": str(e),
                }
        else:
            answer = ""

        return {
            "answer": answer or "（无 LLM 提供者，仅返回检索结果）",
            "sources": self._format_sources(results),
            "chunks": self._format_chunks(results),
            "error": "",
        }

    def search_only(
        self,
        question: str,
        collection_name: str = "default",
        top_k: int = 5,
    ) -> list[SearchResult]:
        """仅搜索，不生成回答"""
        query_vector = self.embedder.get_embedding(question)
        if not query_vector:
            return []
        return self.store.search(collection_name, query_vector, top_k=top_k)

    def _format_context(self, results: list[SearchResult]) -> str:
        """格式化搜索结果上下文"""
        parts = []
        for i, r in enumerate(results, 1):
            heading = r.metadata.get("heading_path", "")
            source_info = f"来源: {heading}" if heading else f"来源: 文档片段 {i}"
            parts.append(f"[{i}] {source_info}")
            parts.append(r.markdown or r.text)
            parts.append("---")
        return "\n".join(parts)

    def _format_sources(self, results: list[SearchResult]) -> list[dict]:
        """格式化来源信息"""
        sources = []
        for r in results:
            sources.append({
                "heading_path": r.metadata.get("heading_path", ""),
                "source_path": r.metadata.get("source_path", ""),
                "score": round(r.score, 4),
                "preview": r.text[:200],
            })
        return sources

    def _format_chunks(self, results: list[SearchResult]) -> list[dict]:
        """格式化分块详情"""
        return [
            {
                "id": r.chunk_id,
                "score": round(r.score, 4),
                "heading_path": r.metadata.get("heading_path", ""),
                "text": r.text,
                "markdown": r.markdown,
            }
            for r in results
        ]
