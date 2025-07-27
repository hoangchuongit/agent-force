from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from api.websocket_handler import handle_websocket
from meta.scenario_injector import ScenarioInjector
from pydantic import BaseModel

from services.openai_client import OpenAIClient
from agents.agent_registry import load_all_agents
from core.debate_manager import DebateManager

app = FastAPI()
injector = ScenarioInjector()

llm = OpenAIClient()
agents = load_all_agents(llm)
manager = DebateManager(agents)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket, manager)

class ScenarioPayload(BaseModel):
    text: str

@app.post("/scenario")
async def submit_scenario(payload: ScenarioPayload):
    scenario = injector.inject(payload.text)
    return {"message": "Scenario injected", "id": scenario.id}