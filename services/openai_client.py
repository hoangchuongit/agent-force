# services/openai_client.py
import os
import time
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


class OpenAIClient:
    """
    Wrapper cho SDK openai>=1.0.0
    - Đọc OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE từ .env hoặc biến môi trường
    - Vẫn cho phép override model/temperature khi khởi tạo thủ công
    """

    def __init__(self, model: str | None = None, temperature: float | None = None):
        load_dotenv()  # nạp file .env (nếu có)

        # Ưu tiên tham số truyền vào; nếu None thì lấy từ env; cuối cùng mới dùng mặc định
        self.model: str = (
            model
            or os.getenv("OPENAI_MODEL")
            or "gpt-4.1-nano"
        )
        self.temperature: float = (
            float(temperature)
            if temperature is not None
            else float(os.getenv("TEMPERATURE", "0.7"))
        )

        # SDK mới: chỉ cần tạo instance, tự đọc OPENAI_API_KEY
        self.client = OpenAI()

    # --------------------- Chat Completion --------------------- #
    def chat(self, prompt: str) -> str:
        """
        Gửi 1 prompt và lấy đáp án dạng text.
        Trả về chuỗi đã strip().
        """
        try:
            print(f"🔍 [Prompt gửi GPT]: {prompt[:120]}…")
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            content = resp.choices[0].message.content
            time.sleep(1.5)  # Mô phỏng độ trễ hiển thị
            return content.strip()

        except OpenAIError as e:
            print(f"⚠️ Lỗi GPT: {e}")
            return "Tôi gặp chút sự cố khi phản hồi."
