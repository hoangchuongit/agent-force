import re
import asyncio, functools
from core.emotion_engine import EmotionEngine
from core.motivation_engine import MotivationEngine
from core.voting import InfluenceScore
from memory.vector_memory import VectorMemory
from memory.memory_timeline import MemoryTimeline
from memory.summarizer import MemorySummarizer
from typing import Optional
from agents.utils.trait_dynamic import DynamicTrait

class BaseAgent:
    def __init__(self, name, role, traits, llm_client, vector_store):
        self.name = name
        self.role = role
        self.traits = {k: DynamicTrait(v) for k, v in traits.items()}
        self.emotion = EmotionEngine()
        self.memory = VectorMemory(name, vector_store)
        self.timeline = MemoryTimeline()
        self.summarizer = MemorySummarizer()
        self.motivation = MotivationEngine()
        self.influence = InfluenceScore()
        self.llm = llm_client

        self.is_muted = False
        self.is_overloaded = False

    def observe(self, context: str):
        self.memory.remember(context)
        self.timeline.add_event(context, self.emotion.current_emotion())
        self.emotion.react_to(context)
        self.motivation.update(context)

    def should_speak(self, context: str) -> bool:
        if self.is_muted or self.is_overloaded:
            return False
        from agents.utils.llm_decider import should_respond
        return should_respond(self, context)


    async def speak(self, context: str) -> dict:
        """Sinh phản hồi bất đồng bộ – gọi OpenAI trong thread pool."""
        # ---- chuẩn bị prompt như cũ ----
        history = self.memory.recall(context)
        summary = self.summarizer.summarize(history)
        emotion_state = self.emotion.current_emotion()
        motivation_state = self.motivation.current_state()
        personality = self.describe_personality()

        prompt = (
            f"Bạn là {self.name} ({self.role}).\n"
            f"Tính cách: {personality}\n"
            f"Cảm xúc hiện tại: {emotion_state}.\n"
            f"Động lực chính: {motivation_state}.\n\n"
            f"Tình huống hiện tại: {context}\n\n"
            f"Tóm tắt ký ức liên quan: {summary}\n\n"
            f"Hãy phản hồi một cách phù hợp với vai trò, tính cách và cảm xúc. "
            f"Kết thúc với kiểu phản hồi bạn chọn trong ngoặc như (phản biện), (giải thích), (hỏi lại), (đồng thuận)..."
        )

        # ---- gọi OpenAI trong executor để không chặn event-loop ----
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,                                 # dùng thread pool mặc định
            functools.partial(self.llm.chat, prompt)
        )

        # ---- lưu memory & phân tích loại câu ----
        self.memory.remember(response)
        self.timeline.add_event(response, emotion_state)

        match = re.search(r"\\((.*?)\\)\\s*$", response)
        speech_type = match.group(1) if match else "không rõ"

        return {
            "text": response.strip(),
            "emotion": emotion_state,
            "motivation": motivation_state,
            "type": speech_type,
            "agent": self.name,
        }


    def reaction_phase(self, previous_speech: str) -> Optional[dict]:
        if not self.should_speak(previous_speech):
            return None

        prompt = (
            f"Một agent vừa phát biểu: '{previous_speech}'\n"
            f"{self.name} có muốn phản ứng lại không? Nếu có, hãy phản hồi ngắn gọn và ghi rõ loại phản ứng trong ngoặc."
        )

        response = self.llm.chat(prompt)
        self.memory.remember(response)
        emotion = self.emotion.current_emotion()
        self.timeline.add_event(response, emotion)

        match = re.search(r"\\((.*?)\\)\\s*$", response)
        speech_type = match.group(1) if match else "reaction"

        return {
            "text": response.strip(),
            "emotion": emotion,
            "type": speech_type,
            "agent": self.name
        }

    def receive_feedback(self, from_agent: str, feedback_type: str):
        feedback_note = f"Nhận phản hồi từ {from_agent}: {feedback_type}"
        self.memory.remember(feedback_note)
        self.timeline.add_event(feedback_note, self.emotion.current_emotion())

        self.emotion.react_to(feedback_type)
        self.motivation.update(feedback_type)

        if feedback_type == "praise":
            self.influence.increase()
        elif feedback_type == "disagree":
            self.influence.decrease()

    def reflect_on_feedback(self, vote_result: bool, peer_feedback: str):
        if vote_result:
            self.traits["logic"].increase(0.05)
            self.traits.setdefault("confidence", DynamicTrait(0.5)).increase(0.1)
        else:
            self.traits["empathy"].increase(0.05)
            self.traits["neuroticism"].increase(0.1)
        self.memory.tag_feedback(peer_feedback)

    def assign_task(self, task: str):
        self.timeline.add_event(f"Assigned: {task}", self.emotion.current_emotion())
        self.memory.remember(f"Được giao việc: {task}")
        return f"Tôi, {self.name}, đã nhận nhiệm vụ: {task}"

    def vote(self, options: list[str], agent_map: dict, prompt: str) -> str:
        return self.motivation.vote_logic(options, agent_map, prompt)

    def describe_personality(self) -> str:
        trait_map = {
            "logic": "lý trí",
            "empathy": "cảm thông",
            "openness": "sáng tạo",
            "conscientiousness": "tận tâm",
            "extraversion": "hướng ngoại",
            "agreeableness": "hợp tác",
            "neuroticism": "dễ xúc động",
            "confidence": "tự tin"
        }
        desc = []
        for k, trait in self.traits.items():
            v = trait.get()
            if v > 0.7:
                desc.append(f"rất {trait_map.get(k, k)}")
            elif v > 0.4:
                desc.append(f"{trait_map.get(k, k)} vừa phải")
            else:
                desc.append(f"ít {trait_map.get(k, k)}")
        return ", ".join(desc)
    
