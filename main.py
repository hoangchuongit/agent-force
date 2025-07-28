from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestrator.crisis import CrisisOrchestrator
from services.llm_client import OpenAIClient

app = FastAPI()
llm = OpenAIClient()
orchestrator = CrisisOrchestrator(llm)

# ✅ Cho phép truy cập từ mọi nguồn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ WebSocket endpoint: stream phản hồi từng dòng
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            async for chunk in orchestrator.stream(user_input):
                await websocket.send_text(chunk)
            await websocket.send_text("[[DONE]]")  # client biết kết thúc
    except Exception as e:
        await websocket.send_text(f"[LỖI WebSocket]: {e}")
        await websocket.close()

# ✅ API (tuỳ chọn) nếu muốn gọi orchestrator qua HTTP POST
class CrisisInput(BaseModel):
    text: str

@app.post("/crisis")
async def handle_crisis(input: CrisisInput):
    results = await orchestrator.run(input.text)
    return results
