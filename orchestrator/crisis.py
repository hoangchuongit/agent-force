
import asyncio
from agents.roles.pragent import PRAgent
from agents.roles.legalagent import LegalAgent
from agents.roles.financeagent import FinanceAgent
from agents.roles.opsagent import OpsAgent

class CrisisOrchestrator:
    def __init__(self, llm_client):
        self.agents = [
            PRAgent(llm_client),
            LegalAgent(llm_client),
            FinanceAgent(llm_client),
            OpsAgent(llm_client)
        ]

    async def run(self, context: str, lightweight: bool = True) -> list[dict]:
        results = []
        for agent in self.agents:
            try:
                response = await agent.speak(context, lightweight)
                results.append(response)
            except Exception as e:
                results.append({
                    "agent": agent.name,
                    "text": f"[LỖI]: {e}",
                    "type": "error"
                })
        return results

    async def stream(self, context: str, lightweight: bool = True):
        for agent in self.agents:
            yield f"\n\n🔹 **{agent.name}** đang phản hồi...\n\n"
            buffer = ""
            try:
                async for chunk in agent.stream_response(context, lightweight):
                    buffer += chunk
                    yield chunk
                yield f"\n\n📝 Tổng kết từ {agent.name}: {buffer.strip()}\n\n---\n"
            except Exception as e:
                yield f"\n[❌ Lỗi khi xử lý {agent.name}]: {e}\n"
