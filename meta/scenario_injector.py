# meta/scenario_injector.py

import uuid
import datetime

class Scenario:
    def __init__(self, description: str, author: str = "judge"):
        self.id = str(uuid.uuid4())
        self.description = description
        self.author = author
        self.timestamp = datetime.datetime.now()

    def as_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "author": self.author,
            "timestamp": self.timestamp.isoformat()
        }


class ScenarioInjector:
    def __init__(self):
        self.scenarios = []

    def inject(self, description: str, author: str = "judge") -> Scenario:
        scenario = Scenario(description=description, author=author)
        self.scenarios.append(scenario)
        print(f"[✅] Scenario injected: {scenario.description}")
        return scenario

    def list_all(self) -> list[dict]:
        return [s.as_dict() for s in self.scenarios]

    def latest(self) -> str:
        if not self.scenarios:
            return ""
        return self.scenarios[-1].description
