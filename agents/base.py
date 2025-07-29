import re
import asyncio, functools
from typing import Optional
from memory.vector_memory import VectorMemory
from memory.summarizer import MemorySummarizer

class BaseAgent:
    def __init__(self, name, role, llm_client, traits=None):
        self.name = name
        self.role = role
        self.llm = llm_client
        self.traits = traits or {}
        self.memory = VectorMemory(agent_name=name)
        self.summarizer = MemorySummarizer()

    def describe_personality(self) -> str:
        trait_map = {
            "logic": "lý trí",
            "empathy": "cảm thông",
            "confidence": "tự tin",
            "neuroticism": "dễ xúc động",
            "agreeableness": "hợp tác"
        }
        desc = []
        for k, v in self.traits.items():
            if v > 0.7:
                desc.append(f"rất {trait_map.get(k, k)}")
            elif v > 0.4:
                desc.append(f"{trait_map.get(k, k)} vừa phải")
            else:
                desc.append(f"ít {trait_map.get(k, k)}")
        return ", ".join(desc) if desc else "lý trí vừa phải, hợp tác vừa phải"

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        summary = self.summarizer.summarize(self.memory.recent_memory(5))
        related = self.memory.recall(context)

        if lightweight:
            prompt = f"Bạn là {self.name} ({self.role}). Tình huống: {context}. Hãy phản hồi phù hợp với vai trò."
        else:
            prompt = (
                f"Bạn là {self.name} ({self.role}).\n"
                f"Tính cách: {self.describe_personality()}.\n"
                f"Tình huống hiện tại: {context}\n"
                f"Ký ức gần đây:{summary}\n"
                f"Ký ức liên quan:{related}\n"
                f"Hãy phản hồi phù hợp với vai trò và ký ức bạn có."
            )

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, functools.partial(self.llm.chat, prompt))

        self.memory.remember(response)

        match = re.search(r"\((.*?)\)\s*$", response)
        speech_type = match.group(1) if match else "n/a"

        return {
            "text": response.strip(),
            "type": speech_type,
            "agent": self.name,
        }

    async def reaction_phase(self, previous_speech: str) -> Optional[dict]:
        prompt = (
            f"Một agent vừa nói: '{previous_speech}'\n"
            f"{self.name} có muốn phản ứng không? Nếu có, hãy phản hồi ngắn và ghi rõ loại phản ứng trong ngoặc."
        )
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, functools.partial(self.llm.chat, prompt))

        self.memory.remember(response)

        match = re.search(r"\((.*?)\)\s*$", response)
        speech_type = match.group(1) if match else "reaction"

        return {
            "text": response.strip(),
            "type": speech_type,
            "agent": self.name
        }

    async def stream_response(self, context: str, lightweight: bool = False):
        summary = self.summarizer.summarize(self.memory.recent_memory(5))
        related = self.memory.recall(context)

        if lightweight:
            prompt = f"Bạn là {self.name} ({self.role}). Tình huống: {context}. Hãy phản hồi phù hợp với vai trò."
        else:
            prompt = (
                f"Bạn là {self.name} ({self.role}).\n"
                f"Tính cách: {self.describe_personality()}.\n"
                f"Tình huống hiện tại: {context}\n"
                f"Ký ức gần đây:\n{summary}\n"
                f"Ký ức liên quan:\n{related}\n"
                f"Hãy phản hồi phù hợp với vai trò và ký ức bạn có."
            )
        async for chunk in self.llm.chat_stream(prompt):
            yield chunk

    def build_review_prompt(self, peer_outputs: dict) -> str:
        peer_view = "\n\n".join(f"- {name}:\n{text}" for name, text in peer_outputs.items())

        return (
            f"Bạn là {self.name} – chuyên gia trong lĩnh vực {self.role}.\n\n"
            f"Các bộ phận khác đã đưa ra các ý kiến sau:\n{peer_view}\n\n"
            "🎯 Yêu cầu:\n"
            "- Nếu **đồng thuận hoàn toàn**, chỉ cần viết: 'Tôi đồng thuận với các ý kiến trên.'\n"
            "- Nếu có **phản biện**, chỉ nêu rõ các điểm cụ thể cần góp ý.\n"
            "- Không tóm tắt lại ý kiến của người khác. Không viết lại toàn bộ nội dung.\n"
            "- Tránh dài dòng. Trả lời súc tích như một chuyên gia.\n\n"
            "✍️ Phản hồi của bạn:"
        )

    async def review_peer_outputs(self, peer_outputs: dict):
        prompt = self.build_review_prompt(peer_outputs)
        async for chunk in self.llm.chat_stream(prompt):
            yield chunk

    async def propose_final_action(self, peer_outputs: dict):
        opinions_text = "\n".join(f"{name}:\n{text}" for name, text in peer_outputs.items())
        prompt = (
            f"Bạn là {self.role}. Sau đây là các ý kiến từ các bộ phận liên quan trong cuộc họp xử lý khủng hoảng:\n\n"
            f"{opinions_text}\n\n"
            f"Dựa trên các ý kiến này, bạn hãy đề xuất phương án hành động cuối cùng (1–3 bước cụ thể) từ góc nhìn của mình."
        )
        async for chunk in self.llm.chat_stream(prompt):
            yield chunk
            
    async def handle_action_stream(self, action: dict):
        message = f"🤖 [{self.name}] Đang xử lý action: {action['type']} → {action.get('content', '')[:50]}..."
        yield message
        # Có thể thêm xử lý mô phỏng thực tế tại đây (gửi API, sinh nội dung, v.v.)
        yield f"✅ [{self.name}] Hoàn tất xử lý: {action['type']}"

