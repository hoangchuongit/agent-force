# vector_store_chroma.py
import re
import uuid
import chromadb

def _slugify(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9._-]', '_', name.strip())
    slug = re.sub(r'_{2,}', '_', slug)
    slug = slug.strip("_.-")
    return slug.lower()[:100]

class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=".chroma")  # ✅ NEW API
        self.collections = {}

    def get_collection(self, agent_name: str):
        slug = _slugify(agent_name)
        if slug not in self.collections:
            self.collections[slug] = self.client.get_or_create_collection(name=slug)
        return self.collections[slug]

    def add_document(self, agent_name: str, content: str, metadata: dict | None = None):
        col = self.get_collection(agent_name)
        doc_id = f"{col.name}_{uuid.uuid4().hex[:8]}"
        metadata = metadata or {"source": "memory"}
        col.add(documents=[content], ids=[doc_id], metadatas=[metadata])

    def query(self, agent_name: str, query: str, top_k: int = 5):
        col = self.get_collection(agent_name)
        res = col.query(query_texts=[query], n_results=top_k)
        return res["documents"][0] if res.get("documents") else []
