
from agents.base import BaseAgent

class OpsAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(
            name="Ops Agent",
            role="vận hành & kỹ thuật",
            llm_client=llm_client,
            traits={'logic': 0.8, 'confidence': 0.6, 'agreeableness': 0.5}
        )

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        context = f"Tình huống kỹ thuật: {context}"
        return await super().speak(context, lightweight)
