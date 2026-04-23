"""MDL 向量存储引擎 - 文件式持久化向量存储与检索"""

import json
import os
import time
import math
from dataclasses import dataclass

from vector_chunker import Chunk


@dataclass
class SearchResult:
    """搜索结果"""
    chunk_id: str
    text: str
    markdown: str
    metadata: dict
    score: float = 0.0


@dataclass
class CollectionEntry:
    """集合中的单个条目"""
    id: str
    text: str
    markdown: str
    metadata: dict
    vector: list[float]


class VectorStoreError(Exception):
    """向量存储错误"""
    pass


class VectorStore:
    """文件式向量存储，纯 Python 余弦相似度搜索"""

    DEFAULT_STORAGE_DIR = os.path.expanduser("~/.mdl/vector_store")

    def __init__(self, storage_dir: str = ""):
        self.storage_dir = storage_dir or self.DEFAULT_STORAGE_DIR
        self._collections: dict[str, dict] = {}  # name -> {entries: list[CollectionEntry], meta: dict}
        self._ensure_storage_dir()
        self._load_index()

    # ── 集合管理 ──

    def list_collections(self) -> list[dict]:
        """列出所有集合信息"""
        result = []
        for name, data in self._collections.items():
            entries = data["entries"]
            meta = data["meta"]
            dim = meta.get("dimension", 0)
            result.append({
                "name": name,
                "chunk_count": len(entries),
                "dimension": dim,
                "created_at": meta.get("created_at", ""),
                "updated_at": meta.get("updated_at", ""),
            })
        return result

    def get_collection_names(self) -> list[str]:
        return list(self._collections.keys())

    def collection_info(self, name: str) -> dict:
        """获取单个集合详情"""
        data = self._collections.get(name)
        if not data:
            raise VectorStoreError(f"集合 '{name}' 不存在")
        entries = data["entries"]
        meta = data["meta"]
        return {
            "name": name,
            "chunk_count": len(entries),
            "dimension": meta.get("dimension", 0),
            "created_at": meta.get("created_at", ""),
            "updated_at": meta.get("updated_at", ""),
            "has_embeddings": bool(entries and entries[0].vector),
        }

    def create_collection(self, name: str, dimension: int = 0):
        """创建新集合"""
        if name in self._collections:
            raise VectorStoreError(f"集合 '{name}' 已存在")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self._collections[name] = {
            "entries": [],
            "meta": {
                "dimension": dimension,
                "created_at": now,
                "updated_at": now,
            },
        }
        self._save_index()

    def delete_collection(self, name: str) -> bool:
        """删除集合"""
        if name not in self._collections:
            return False
        del self._collections[name]
        coll_path = self._collection_path(name)
        if os.path.exists(coll_path):
            os.remove(coll_path)
        self._save_index()
        return True

    def collection_exists(self, name: str) -> bool:
        return name in self._collections

    # ── 数据操作 ──

    def add_chunks(self, collection_name: str, chunks: list[Chunk],
                   embeddings: list[list[float]]) -> int:
        """添加分块及对应向量到集合"""
        if collection_name not in self._collections:
            dim = len(embeddings[0]) if embeddings else 0
            self.create_collection(collection_name, dim)

        data = self._collections[collection_name]
        existing_ids = {e.id for e in data["entries"]}
        count = 0
        for chunk, vector in zip(chunks, embeddings):
            if chunk.id in existing_ids:
                continue
            if not vector:
                continue
            entry = CollectionEntry(
                id=chunk.id,
                text=chunk.text,
                markdown=chunk.markdown,
                metadata=chunk.metadata,
                vector=vector,
            )
            data["entries"].append(entry)
            existing_ids.add(chunk.id)
            count += 1

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        data["meta"]["updated_at"] = now
        if data["meta"].get("dimension", 0) == 0 and embeddings:
            data["meta"]["dimension"] = len(embeddings[0])

        self.save_collection(collection_name)
        return count

    def search(self, collection_name: str, query_vector: list[float],
               top_k: int = 5) -> list[SearchResult]:
        """余弦相似度搜索"""
        data = self._collections.get(collection_name)
        if not data:
            raise VectorStoreError(f"集合 '{collection_name}' 不存在")
        entries = data["entries"]
        if not entries:
            return []

        scored = []
        for entry in entries:
            if not entry.vector:
                continue
            score = self.cosine_similarity(query_vector, entry.vector)
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, entry in scored[:top_k]:
            results.append(SearchResult(
                chunk_id=entry.id,
                text=entry.text,
                markdown=entry.markdown,
                metadata=entry.metadata,
                score=score,
            ))
        return results

    def count(self, collection_name: str) -> int:
        data = self._collections.get(collection_name)
        return len(data["entries"]) if data else 0

    def get_chunks(self, collection_name: str) -> list[CollectionEntry]:
        """获取集合中所有分块"""
        data = self._collections.get(collection_name)
        return list(data["entries"]) if data else []

    # ── 持久化 ──

    def save_collection(self, name: str):
        """保存集合到磁盘"""
        data = self._collections.get(name)
        if not data:
            return
        serializable = {
            "meta": data["meta"],
            "entries": [
                {
                    "id": e.id,
                    "text": e.text,
                    "markdown": e.markdown,
                    "metadata": e.metadata,
                    "vector": e.vector,
                }
                for e in data["entries"]
            ],
        }
        path = self._collection_path(name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        self._save_index()

    def load_collection(self, name: str):
        """从磁盘加载集合"""
        path = self._collection_path(name)
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            entries = []
            for e_raw in raw.get("entries", []):
                entry = CollectionEntry(
                    id=e_raw["id"],
                    text=e_raw.get("text", ""),
                    markdown=e_raw.get("markdown", ""),
                    metadata=e_raw.get("metadata", {}),
                    vector=e_raw.get("vector", []),
                )
                entries.append(entry)
            meta = raw.get("meta", {})
            self._collections[name] = {"entries": entries, "meta": meta}
        except Exception as e:
            print(f"[MDL] 加载集合 '{name}' 失败: {e}")

    def export_collection(self, name: str, path: str):
        """导出集合到独立 JSON 文件"""
        data = self._collections.get(name)
        if not data:
            raise VectorStoreError(f"集合 '{name}' 不存在")
        export_data = {
            "collection": name,
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "meta": data["meta"],
            "entries": [
                {
                    "id": e.id,
                    "text": e.text,
                    "markdown": e.markdown,
                    "metadata": e.metadata,
                    "vector": e.vector,
                }
                for e in data["entries"]
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def import_collection(self, name: str, path: str):
        """从导出文件导入集合"""
        if not os.path.exists(path):
            raise VectorStoreError(f"导入文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        entries = []
        for e_raw in raw.get("entries", []):
            entry = CollectionEntry(
                id=e_raw["id"],
                text=e_raw.get("text", ""),
                markdown=e_raw.get("markdown", ""),
                metadata=e_raw.get("metadata", {}),
                vector=e_raw.get("vector", []),
            )
            entries.append(entry)
        meta = raw.get("meta", {})
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        meta["imported_at"] = now
        self._collections[name] = {"entries": entries, "meta": meta}
        self.save_collection(name)

    # ── 内部 ──

    def _ensure_storage_dir(self):
        os.makedirs(self.storage_dir, exist_ok=True)

    def _index_path(self) -> str:
        return os.path.join(self.storage_dir, "index.json")

    def _collection_path(self, name: str) -> str:
        return os.path.join(self.storage_dir, f"{name}.json")

    def _load_index(self):
        """加载 index.json 并自动加载所有集合"""
        idx_path = self._index_path()
        if not os.path.exists(idx_path):
            return
        try:
            with open(idx_path, "r", encoding="utf-8") as f:
                index = json.load(f)
            collections = index.get("collections", {})
            for name in collections:
                self.load_collection(name)
        except Exception as e:
            print(f"[MDL] 加载向量索引失败: {e}")

    def _save_index(self):
        index = {
            "storage_dir": self.storage_dir,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "collections": {},
        }
        for name, data in self._collections.items():
            index["collections"][name] = {
                "chunk_count": len(data["entries"]),
                "dimension": data["meta"].get("dimension", 0),
                "created_at": data["meta"].get("created_at", ""),
                "updated_at": data["meta"].get("updated_at", ""),
            }
        with open(self._index_path(), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    # ── 数学 ──

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """纯 Python 余弦相似度"""
        if not a or not b:
            return 0.0
        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for x, y in zip(a, b):
            dot_product += x * y
            norm_a += x * x
            norm_b += y * y
        denom = math.sqrt(norm_a) * math.sqrt(norm_b)
        if denom == 0:
            return 0.0
        return dot_product / denom
