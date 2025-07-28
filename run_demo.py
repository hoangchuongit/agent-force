import asyncio
import yaml
import sys
from orchestrator.crisis import CrisisOrchestrator
from services.llm_client import OpenAIClient

def load_cases(path="cases/test_cases.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

async def run_demo(case_id=None):
    cases = load_cases()
    selected = cases[0] if not case_id else next((c for c in cases if c["id"] == case_id), None)
    if not selected:
        print(f"❌ Không tìm thấy tình huống với ID: {case_id}")
        return

    print(f"🔎 Xử lý tình huống: {selected['title']}")
    print(f"📄 Mô tả: {selected['description']}\n")

    orchestrator = CrisisOrchestrator(OpenAIClient())
    async for chunk in orchestrator.stream(selected["description"]):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    case_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_demo(case_id))
