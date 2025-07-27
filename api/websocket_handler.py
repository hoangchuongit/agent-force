from fastapi import WebSocket, WebSocketDisconnect
from core.debate_manager import DebateManager

async def handle_websocket(ws: WebSocket, manager: DebateManager) -> None:
    await ws.accept()
    await ws.send_text("🤖 Kết nối thành công với AgentForce!")

    try:
        while True:
            user_msg = await ws.receive_text()

            # ⬇⬇  STREAM   ⬇⬇
            async for msg in manager.debate_flow(user_msg, False):
                await ws.send_text(msg)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("❌ WebSocket lỗi:", e)
    finally:
        await ws.close()
