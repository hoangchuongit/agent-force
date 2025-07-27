class SpeechStyle:
    def __init__(self, personality):
        self.personality = personality

    def generate_prompt(self, name, context, emotion, motivation, belief_system):
        tone = "thân thiện" if self.personality.traits["agreeableness"] > 0.5 else "thẳng thắn"
        return f"[{name} - {tone} - {emotion.state}] Tôi nghĩ rằng: {context}"
