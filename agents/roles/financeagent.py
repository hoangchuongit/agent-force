
from agents.base import BaseAgent
from agents.config import AGENT_PERSONALITIES

class FinanceAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(
            name="Finance Agent",
            role="tài chính doanh nghiệp",
            llm_client=llm_client,
            traits={'logic': 0.85, 'confidence': 0.7, 'agreeableness': 0.4},
            personality_prompt=AGENT_PERSONALITIES.get("Finance", "")
        )

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        context = f"Tình huống tài chính: {context}"
        return await super().speak(context, lightweight)
