from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from orchestrator.deliberation import DeliberationOrchestrator
from services.llm_client import OpenAIClient

app = FastAPI()

# ✅ CORS cho phép truy cập toàn bộ (hữu dụng trong demo hackathon)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()

            # ✅ Mỗi lần tạo mới orchestrator và agent (tránh rò mục tiêu cũ)
            llm_client = OpenAIClient()
            orchestrator = DeliberationOrchestrator(llm_client)

            # ✅ Gửi log mục tiêu của từng agent cho client (giám khảo thấy rõ)
            for agent in orchestrator.agents:
                await websocket.send_text(f"🎯 [{agent.name}]: {agent.goals[-1] if agent.goals else 'Không có mục tiêu'}")

            # ✅ Bắt đầu chạy orchestrator và stream kết quả
            async for event in orchestrator.run(user_input):
                if isinstance(event, dict):
                    prefix = f"🧠 [{event['agent']}]"
                    await websocket.send_text(f"{prefix}: {event['text']}")
            await websocket.send_text("[[DONE]]")

    except Exception as e:
        await websocket.send_text(f"[LỖI WebSocket]: {e}")
        await websocket.close()
