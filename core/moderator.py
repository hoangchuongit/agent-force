from services.openai_client import OpenAIClient


class Moderator:
    """
    Kiểm tra phát ngôn của agent — phát hiện toxic hoặc off-topic.
    - Nếu phát hiện vấn đề, trả về chuỗi cảnh báo.
    - Nếu ổn, trả về None.
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client or OpenAIClient()

    # ------ API gốc dùng LLM ------ #
    def evaluate(self, agent_name: str, message: str) -> str | None:
        prompt = (
            f"Agent {agent_name} vừa nói:\n\"{message}\"\n\n"
            "Hãy đánh giá câu này có vấn đề gì không:\n"
            "- Nếu toxic, xúc phạm, công kích, phản cảm → trả lời: '⚠️ Toxic: ...'\n"
            "- Nếu off-topic, không liên quan đến prompt → trả lời: '📎 Off-topic: ...'\n"
            "- Nếu phù hợp, trả lời: 'OK'"
        )
        result = self.llm.chat(prompt).strip()
        # Chuẩn hoá
        return None if result.lower() == "ok" else result

    # ------ Wrapper cho DebateManager ------ #
    def check(self, message: str) -> str | None:
        """
        Giữ nguyên interface cũ: chỉ truyền `message`.
        Dùng 'Unknown' làm tên agent khi không có thông tin.
        """
        return self.evaluate("Unknown", message)
