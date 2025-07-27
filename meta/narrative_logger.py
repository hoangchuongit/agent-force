import datetime

class NarrativeLogger:
    def __init__(self):
        self.logs = []
        self.turn = 0

    def start_new_turn(self, user_prompt: str):
        self.turn += 1
        self.logs.append({
            "turn": self.turn,
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": user_prompt,
            "responses": [],
            "moderator_flags": [],
            "votes": {},
            "task_assignments": []  # 👈 thêm mặc định
        })

    def log_response(self, agent_name: str, response: str):
        self.logs[-1]["responses"].append({
            "agent": agent_name,
            "text": response
        })

    def log_moderator_flag(self, agent_name: str, issue: str):
        self.logs[-1]["moderator_flags"].append({
            "agent": agent_name,
            "issue": issue
        })

    def log_votes(self, vote_result: dict):
        self.logs[-1]["votes"] = vote_result

    def log_task_assignment(self, agent_name: str, message: str):
        self.logs[-1]["task_assignments"].append({
            "agent": agent_name,
            "message": message
        })

    def export_text(self):
        result = ""
        for turn in self.logs:
            result += f"\n🌀 Turn {turn['turn']} – {turn['timestamp']}\n"
            result += f"📝 Prompt: {turn['prompt']}\n"
            for r in turn["responses"]:
                result += f"🧠 {r['agent']}: {r['text']}\n"
            for flag in turn["moderator_flags"]:
                result += f"⚠️ Moderator flagged {flag['agent']}: {flag['issue']}\n"
            if turn["task_assignments"]:
                result += "📌 Giao việc:\n"
                for task in turn["task_assignments"]:
                    result += f"   - {task['agent']}: {task['message']}\n"
            result += "🗳️ Voting:\n"
            for k, v in turn["votes"].items():
                result += f"   - {k}: {v} votes\n"
        return result

    def reset(self):
        self.logs = []
        self.turn = 0
