
import time
from openai import OpenAI, OpenAIError
from config import OPENAI_MODEL, TEMPERATURE

class OpenAIClient:
    """
    LLM client chuẩn cho dự án Crisis Response
    - Hỗ trợ chat() sync
    - Hỗ trợ chat_stream() async generator
    - Dùng config.py để load cấu hình model
    """

    def __init__(self, model: str | None = None, temperature: float | None = None):
        self.model = model or OPENAI_MODEL
        self.temperature = temperature if temperature is not None else TEMPERATURE
        self.client = OpenAI()

    def chat(self, prompt: str) -> str:
        """Gửi prompt và trả về chuỗi phản hồi đầy đủ."""
        try:
            print(f"🔍 [Prompt gửi GPT]: {prompt[:120]}…")
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            content = resp.choices[0].message.content
            time.sleep(1.0)  # mô phỏng độ trễ thực tế
            return content.strip()
        except OpenAIError as e:
            print(f"⚠️ Lỗi GPT: {e}")
            return "Tôi gặp chút sự cố khi phản hồi."

    async def chat_stream(self, prompt: str):
        """Trả về phản hồi theo dòng (dạng async generator)"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except OpenAIError as e:
            yield f"[LỖI khi stream GPT]: {e}"
