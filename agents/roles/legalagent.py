
from agents.base import BaseAgent

class LegalAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(
            name="Legal Agent",
            role="pháp lý & tuân thủ",
            llm_client=llm_client,
            traits={'logic': 0.9, 'confidence': 0.7, 'agreeableness': 0.3}
        )

    async def speak(self, context: str, lightweight: bool = False) -> dict:
        context = f"Tình huống pháp lý: {context}"
        return await super().speak(context, lightweight)
