class MotivationEngine:
    def __init__(self):
        self.level = 0.5  # Default

    def adjust(self, feedback):
        if "positive" in feedback:
            self.level = min(1.0, self.level + 0.1)
        else:
            self.level = max(0.0, self.level - 0.1)
