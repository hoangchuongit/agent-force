# memory/vector_store_chroma.py
import re
import chromadb
from chromadb.config import Settings


def _slugify(name: str) -> str:
    """
    Biến 'Dev Duy' → 'dev_duy' để dùng làm tên collection.
    Chỉ giữ ký tự a-z, A-Z, 0-9, '.', '_', '-'
    """
    slug = re.sub(r'[^a-zA-Z0-9._-]', '_', name.strip())
    slug = re.sub(r'_{2,}', '_', slug)  # gộp nhiều dấu _ liên tiếp
    slug = slug.strip("_.-")            # bỏ ký tự đặc biệt đầu/cuối
    return slug.lower()[:100]           # tối đa 100 kí tự


class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.Client(Settings())
        self.collections = {}

    # ---------- COLLECTION ---------- #
    def get_collection(self, agent_name: str):
        slug = _slugify(agent_name)
        if slug not in self.collections:
            self.collections[slug] = self.client.get_or_create_collection(name=slug)
        return self.collections[slug]

    # ---------- WRITE ---------- #
    def add_document(
        self,
        agent_name: str,
        content: str,
        metadata: dict | None = None,
    ):
        col = self.get_collection(agent_name)
        doc_id = f"{col.name}_{col.count()}"

        # 👉 bảo đảm metadata non-empty
        if not metadata:
            metadata = {"source": "memory"}

        col.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata],
        )

    # ---------- READ ---------- #
    def query(self, agent_name: str, query: str, top_k: int = 5):
        col = self.get_collection(agent_name)
        res = col.query(query_texts=[query], n_results=top_k)
        return res["documents"][0] if res["documents"] else []
