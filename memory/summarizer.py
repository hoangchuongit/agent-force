# memory/summarizer.py

from services.llm_client import OpenAIClient

class MemorySummarizer:
    def __init__(self):
        self.llm = OpenAIClient() 

    def summarize(self, history_list: list[str]) -> str:
        if not history_list:
            return "Không có gì để tóm tắt."

        history_text = "\n".join(f"- {entry}" for entry in history_list)
        prompt = (
            "Tóm tắt nội dung hội thoại sau đây dưới dạng ngắn gọn, dễ hiểu, mô tả cảm xúc và chủ đề chính:\n"
            f"{history_text[:2000]}"
        )
        return self.llm.chat(prompt)
