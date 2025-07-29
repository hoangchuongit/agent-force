from agents.base import BaseAgent
from agents.config import AGENT_PERSONALITIES

class CriticalAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(
            name="Critical Agent",
            role="phản biện độc lập",
            llm_client=llm_client,
            traits={'logic': 0.9, 'confidence': 0.85, 'agreeableness': 0.2},
            personality_prompt=AGENT_PERSONALITIES.get("Critical", "")
        )

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        context = f"Tình huống đang tranh luận: {context}"
        return await super().speak(context, lightweight)
