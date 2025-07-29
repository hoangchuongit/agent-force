# orchestrator/executor.py
from typing import List, Dict
from agents.roles.pragent import PRAgent
from agents.roles.legalagent import LegalAgent
from agents.roles.financeagent import FinanceAgent
from agents.roles.opsagent import OpsAgent

AGENT_MAP = {
    "PR": PRAgent,
    "Legal": LegalAgent,
    "Finance": FinanceAgent,
    "Ops": OpsAgent
}

ALLOWED_ACTION_TYPES = {"send_email", "notify", "create_ticket"}  # 🎯 Chỉ cho phép 3 loại hành động

async def execute_actions_stream(llm_client, actions: List[Dict]):
    print("\n🚀 Thực thi các hành động đã thống nhất:")
    for action in actions:
        agent_key = action.get("assigned_agent")
        action_type = action.get("type")

        if action_type not in ALLOWED_ACTION_TYPES:
            print(f"⚠️ Bỏ qua hành động không được hỗ trợ: {action_type}")
            continue

        if agent_key not in AGENT_MAP:
            print(f"⚠️ Bỏ qua hành động không thuộc phạm vi agent hỗ trợ: {agent_key}")
            continue

        agent_cls = AGENT_MAP[agent_key]
        agent_instance = agent_cls(llm_client)
        print(f"\n🔸 [Action] {action_type} → Giao cho {agent_key} Agent")
        async for chunk in agent_instance.handle_action_stream(action):
            yield chunk
