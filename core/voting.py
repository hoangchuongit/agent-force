# core/voting.py

class InfluenceScore:
    def __init__(self):
        self.score = 0.0

    def increase(self, amount=1.0):
        self.score += amount

    def decrease(self, amount=1.0):
        self.score -= amount

    def current(self):
        return self.score


def vote_winner(agent, utterances: dict) -> str:
    """
    Agent sẽ vote cho phát biểu hay nhất trong danh sách utterances.

    utterances = {
        "Phuong": "Tôi nghĩ rằng nên tập trung vào người dùng...",
        "Duy": "Giải pháp công nghệ này scale rất tốt...",
        ...
    }
    """
    from random import choice

    options = [k for k in utterances.keys() if k != agent.name]
    if not options:
        return None

    prompt = (
        f"Bạn là {agent.name} ({agent.role}). Dưới đây là các ý kiến từ những người khác:\n\n"
    )

    for name, speech in utterances.items():
        if name != agent.name:
            prompt += f"- {name}: \"{speech}\"\n"

    prompt += (
        "\nDựa trên tính cách và logic, bạn thấy ai có ý tưởng tốt nhất? "
        "Chỉ trả lời tên người đó."
    )

    response = agent.llm.chat(prompt).strip()
    return response if response in options else choice(options)


# ✅ THÊM PHẦN NÀY VÀO ĐỂ TRÁNH LỖI IMPORT
class VotingEngine:
    def vote(self, agents, round_responses: list[str]) -> dict:
        """
        agents: List[Agent]
        round_responses: List[str] like ["🧠 Duy: Nội dung..."]

        Return:
            Dict[agent_name -> voted_person_name]
        """
        utterances = {}
        for line in round_responses:
            if ": " in line:
                name, content = line.replace("🧠", "").strip().split(": ", 1)
                utterances[name.strip()] = content.strip()

        results = {}
        for agent in agents:
            voted = vote_winner(agent, utterances)
            results[agent.name] = voted
        return results
