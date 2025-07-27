class BeliefSystem:
    def __init__(self):
        self.beliefs = {}

    def update(self, feedback):
        self.beliefs["last_feedback"] = feedback
