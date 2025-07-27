from memory.vector_store_chroma import ChromaVectorStore

class VectorMemory:
    def __init__(self, agent_name: str, vector_backend=None):
        self.agent_name = agent_name
        self.vector_backend = vector_backend or ChromaVectorStore()
        self.local_history: list[str] = []

    def remember(self, content: str):
        """Ghi nhớ thông tin mới vào local + vector backend"""
        self.local_history.append(content)
        self.vector_backend.add_document(agent_name=self.agent_name, content=content)

    def recall(self, query: str, top_k: int = 5) -> str:
        """Truy xuất trí nhớ liên quan từ vector backend"""
        docs = self.vector_backend.query(
            agent_name=self.agent_name,
            query=query,
            top_k=top_k
        )
        return "\n".join(docs) if docs else "Không có ký ức liên quan."

    def recent_memory(self, n: int = 5) -> list[str]:
        """Lấy ra các dòng nhớ gần nhất"""
        return self.local_history[-n:]

    def tag_feedback(self, feedback: str):
        """Gắn feedback để học từ phản hồi"""
        self.vector_backend.add_document(
            agent_name=self.agent_name,
            content=f"[Feedback]: {feedback}",
            metadata={"type": "feedback"}
        )

def get_default_vector_store():
    return ChromaVectorStore()