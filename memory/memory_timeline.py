# memory/memory_timeline.py

from datetime import datetime

class MemoryTimeline:
    def __init__(self):
        self.timeline = []

    def add_event(self, event: str, emotion: str = None):
        self.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "emotion": emotion
        })

    def recall_recent(self, n: int = 3):
        return self.timeline[-n:]

    def full_timeline(self):
        return self.timeline

    def __str__(self):
        lines = []
        for item in self.timeline:
            emo = f" 😐 [{item['emotion']}]" if item['emotion'] else ""
            lines.append(f"{item['timestamp']}: {item['event']}{emo}")
        return "\n".join(lines)
