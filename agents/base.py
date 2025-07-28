
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
