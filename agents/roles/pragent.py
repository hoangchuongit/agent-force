
from agents.base import BaseAgent

class PRAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(
            name="PR Agent",
            role="truyền thông & quan hệ công chúng",
            llm_client=llm_client,
            traits={'empathy': 0.8, 'agreeableness': 0.75, 'confidence': 0.6}
        )

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        context = f"Tình huống truyền thông: {context}"
        return await super().speak(context, lightweight)
