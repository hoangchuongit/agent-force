class EmotionEngine:
    def __init__(self, state="neutral"):
        self.state = state

    def should_express(self, personality):
        return self.state in ["excited", "angry"] or personality.traits["extraversion"] > 0.6

    def update(self, feedback):
        if "support" in feedback:
            self.state = "happy"
        elif "rejected" in feedback:
            self.state = "angry"
