import random

class LangGraphEngine:
    def __init__(self, agents: list):
        self.agents = agents

    def run_round(self, context: str) -> list[tuple[str, str]]:
        """
        Mỗi agent tự quyết định có nói không.
        Trả về danh sách (agent_name, response)
        """
        responses = []
        random.shuffle(self.agents)  # Để tranh luận tự nhiên hơn

        for agent in self.agents:
            if agent.should_speak(context):
                reply = agent.speak(context)
                responses.append((agent.name, reply))

                # Các agent còn lại ghi nhận
                for other in self.agents:
                    if other.name != agent.name:
                        other.observe(f"{agent.name} nói: {reply}")

        return responses
