import re
import asyncio, functools
from typing import Optional
from memory.vector_memory import VectorMemory
from memory.summarizer import MemorySummarizer

class BaseAgent:
    def __init__(self, name, role, llm_client, traits=None, personality_prompt=None):
        self.name = name
        self.role = role
        self.llm = llm_client
        self.traits = traits or {}
        self.personality_prompt = personality_prompt  # tách khỏi describe_personality()
        self.memory = VectorMemory(agent_name=name)
        self.summarizer = MemorySummarizer()
        self.goals = []

    def describe_personality(self) -> str:
        if self.personality_prompt:
            return self.personality_prompt

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
        return ", ".join(desc) if desc else "trung lập và hợp tác vừa phải"

    def get_goal_context(self):
        if not self.goals:
            return ""
        return "Mục tiêu hiện tại của bạn là:\n" + "\n".join(f"- {g}" for g in self.goals) + "\n"

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        summary = self.summarizer.summarize(self.memory.recent_memory(5))
        related = self.memory.recall(context)

        if lightweight:
            prompt = f"Bạn là {self.name} ({self.role}). Tình huống: {context}. Hãy phản hồi phù hợp với vai trò."
        else:
            prompt = (
                f"Bạn là {self.name} ({self.role}).\n"
                f"Tính cách: {self.describe_personality()}.\n"
                f"{self.get_goal_context()}"
                f"Tình huống hiện tại: {context}\n"
                f"Ký ức gần đây:\n{summary}\n"
                f"Ký ức liên quan:\n{related}\n"
                f"Hãy phản hồi phù hợp với vai trò, mục tiêu và tính cách cá nhân."
            )

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, functools.partial(self.llm.chat, prompt))

        self.memory.remember(response)

        match = re.search(r"\\((.*?)\\)\\s*$", response)
        speech_type = match.group(1) if match else "n/a"

        return {
            "text": response.strip(),
            "type": speech_type,
            "agent": self.name,
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
                f"{self.get_goal_context()}"
                f"Tình huống hiện tại: {context}\n"
                f"Ký ức gần đây:\n{summary}\n"
                f"Ký ức liên quan:\n{related}\n"
                f"Hãy phản hồi phù hợp với vai trò, mục tiêu và tính cách cá nhân."
            )
        async for chunk in self.llm.chat_stream(prompt):
            yield chunk

    async def reaction_phase(self, previous_speech: str) -> Optional[dict]:
        prompt = (
            f"{self.name} ({self.role}) đang theo dõi cuộc họp.\n"
            f"Một agent vừa phát biểu: '{previous_speech}'\n"
            f"Với phong cách {self.describe_personality()}, bạn có muốn phản ứng không?\n"
            f"Nếu có, hãy phản hồi ngắn gọn và ghi rõ loại phản ứng trong ngoặc."
        )
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, functools.partial(self.llm.chat, prompt))

        self.memory.remember(response)

        match = re.search(r"\\((.*?)\\)\\s*$", response)
        speech_type = match.group(1) if match else "reaction"

        return {
            "text": response.strip(),
            "type": speech_type,
            "agent": self.name
        }

    def build_review_prompt(self, peer_outputs: dict) -> str:
        peer_view = "\n\n".join(f"- {name}:\n{text}" for name, text in peer_outputs.items())

        return (
            f"Bạn là {self.name} – chuyên gia trong lĩnh vực {self.role}.\n"
            f"Phong cách cá nhân: {self.describe_personality()}\n"
            f"\nCác bộ phận khác đã đưa ra các ý kiến sau:\n{peer_view}\n\n"
            "🎯 Yêu cầu:\n"
            "- Nếu **đồng thuận hoàn toàn**, chỉ cần viết: 'Tôi đồng thuận với các ý kiến trên.'\n"
            "- Nếu có **phản biện**, hãy thể hiện quan điểm theo phong cách riêng.\n"
            "- Không lặp lại nội dung của người khác.\n"
            "- Trả lời ngắn gọn, sắc sảo như một chuyên gia.\n\n"
            "✍️ Phản hồi của bạn:"
        )

    async def review_peer_outputs(self, peer_outputs: dict):
        prompt = self.build_review_prompt(peer_outputs)
        async for chunk in self.llm.chat_stream(prompt):
            yield chunk

    async def handle_action_stream(self, action: dict):
        message = f"🤖 [{self.name}] Đang xử lý action: {action['type']} → {action.get('content', '')[:50]}..."
        yield message
        # Có thể thêm xử lý mô phỏng thực tế tại đây (gửi API, sinh nội dung, v.v.)
        yield f"✅ [{self.name}] Hoàn tất xử lý: {action['type']}"

    def set_goal(self, goal_text: str):
        self.goals.append(goal_text)

    def clear_goals(self):
        self.goals = []
