class MotivationEngine:
    def __init__(self):
        self.motivations = {
            "giải quyết vấn đề": 0.5,
            "giữ hòa khí": 0.5,
            "khẳng định quan điểm": 0.5
        }

    def update(self, context: str):
        if "mâu thuẫn" in context or "tranh cãi" in context:
            self.motivations["giữ hòa khí"] += 0.1
        if "đề xuất" in context or "giải pháp" in context:
            self.motivations["giải quyết vấn đề"] += 0.2
        if "không đồng ý" in context:
            self.motivations["khẳng định quan điểm"] += 0.2
        self._clamp()

    def current_state(self) -> str:
        sorted_motives = sorted(self.motivations.items(), key=lambda x: -x[1])
        return sorted_motives[0][0]

    def vote_logic(self, options: list[str], agent_map: dict, prompt: str) -> str:
        """
        Chọn agent phù hợp với động lực & ngữ cảnh prompt.
        """
        motive = self.current_state().lower()

        def relevance(agent_name: str) -> float:
            score = 0.0
            if motive in agent_name.lower():
                score += 1.0
            agent = agent_map.get(agent_name)
            if agent and motive in agent.role.lower():
                score += 1.5
            if agent and motive in agent.describe_personality():
                score += 1.5
            return score

        ranked = sorted(options, key=lambda n: relevance(n), reverse=True)
        return ranked[0] if ranked else options[0]

    def _clamp(self):
        for key in self.motivations:
            self.motivations[key] = max(0.0, min(1.0, self.motivations[key]))
