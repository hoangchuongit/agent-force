import asyncio
import sys
import yaml
import os
from datetime import datetime
from orchestrator.deliberation import DeliberationOrchestrator
from services.llm_client import OpenAIClient

def load_cases(path="cases/test_cases.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_log(case_id: str, content: str):
    log_dir = ".logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"{case_id}_{timestamp}.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n📁 Log đã được lưu tại: {log_path}")

async def run_demo(case_id=None):
    cases = load_cases()
    selected = cases[0] if not case_id else next((c for c in cases if c["id"] == case_id), None)
    if not selected:
        print(f"❌ Không tìm thấy tình huống với ID: {case_id}")
        return

    print(f"🔎 Xử lý tình huống: {selected['title']}")
    print(f"📄 Mô tả: {selected['description']}\n")

    orchestrator = DeliberationOrchestrator(OpenAIClient())
    log_buffer = []
    
    async for result in orchestrator.run(selected["description"]):
        # Bỏ qua stream để không in từng chữ
        if result["type"].startswith("stream_"):
            continue
        
        prefix = f"\n🔹 [{result['type']}] {result['agent']}:"
        output = f"{prefix}\n{result['text']}\n" + "-" * 50
        print(output)
        log_buffer.append(output)

    # Ghi file log
    case_log_id = selected.get("id", "demo")
    save_log(case_log_id, "\n".join(log_buffer))

if __name__ == "__main__":
    case_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_demo(case_id))
