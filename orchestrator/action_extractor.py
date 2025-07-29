# orchestrator/action_extractor.py
from typing import AsyncGenerator, Dict

PROMPT = """
Bạn là trợ lý phân tích hành động. Dưới đây là một bản đề xuất thống nhất:
---
{proposal}
---
🎯 Yêu cầu:
- Chỉ trích xuất các hành động có thể thực thi được, thuộc đúng 1 trong 3 loại sau:
  • "send_email"
  • "create_ticket" (Jira)
  • "notify" (Slack)
- Mỗi hành động phải bao gồm trường: type, content/message, assigned_agent (1 trong: PR, Legal, Finance, Ops).
- Không tạo hành động ngoài 3 loại trên. Không dùng các loại như: lên lịch, huấn luyện, phân công, đánh giá, báo cáo, lập kế hoạch...
- Kết quả định dạng JSON như sau:

[
  {{ "type": "send_email", "recipient": "...", "content": "...", "assigned_agent": "PR" }},
  {{ "type": "create_ticket", "system": "Jira", "content": "...", "assigned_agent": "Ops" }},
  {{ "type": "notify", "channel": "Slack", "target": "Legal", "message": "...", "assigned_agent": "Legal" }}
]

Chỉ xuất ra JSON, không giải thích, không văn bản thừa.
"""

async def extract_actions_stream(llm_client, final_proposal: str) -> AsyncGenerator[str, None]:
    prompt = PROMPT.format(proposal=final_proposal)
    async for chunk in llm_client.chat_stream(prompt):
        yield chunk