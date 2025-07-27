from collections import Counter
import asyncio
from typing import List, Optional, AsyncIterator

from core.moderator import Moderator
from core.voting import VotingEngine
from meta.narrative_logger import NarrativeLogger
from meta.influence_tracker import InfluenceTracker


class DebateManager:
    """Điều phối tranh luận giữa nhiều agent – stream từng thông điệp, hỗ trợ chạy song song."""

    def __init__(self, agents: List, logger: Optional[NarrativeLogger] = None):
        self.agents = agents
        self.voting = VotingEngine()
        self.moderator = Moderator()
        self.logger = logger or NarrativeLogger()
        self.influence = InfluenceTracker()
        self.round_num = 1
        self.assigned_agent = None  # nhớ agent được giao nhiệm vụ

    def reset_assignment(self):
        self.assigned_agent = None

    # ------------------------------------------------------------------
    # STREAMING API
    # ------------------------------------------------------------------
    async def debate_flow(
        self,
        user_prompt: str,
        quick_mode: bool = False,
    ) -> AsyncIterator[str]:
        """
        Async-generator: yield message ngay khi sẵn sàng.
        quick_mode=True  ➜ dừng luồng sau khi giao task cho winner.
        """

        # 1️⃣ Bắt đầu lượt ------------------------------------------------
        self.logger.start_new_turn(user_prompt)
        for ag in self.agents:
            ag.observe(user_prompt)

        # 2️⃣ Tạo task speak() song song --------------------------------
        tasks = []
        task_agent_map = {}

        candidate_agents = (
            [self.assigned_agent] if self.assigned_agent and self.assigned_agent.should_speak(user_prompt)
            else self.agents
        )

        for ag in candidate_agents:
            if ag.should_speak(user_prompt):
                task = asyncio.create_task(ag.speak(user_prompt))
                tasks.append(task)
                task_agent_map[task] = ag

        for completed_task in asyncio.as_completed(tasks):
            try:
                resp = await completed_task
                ag = task_agent_map[completed_task]
                text = resp["text"]
                self.logger.log_response(ag.name, text)
                yield f"🧠 {ag.name}: {text}"

                warn = self.moderator.evaluate(ag.name, text)
                if warn:
                    self.logger.log_moderator_flag(ag.name, warn)
                    yield f"⚠️ Moderator: {warn}"
            except Exception as e:
                ag = task_agent_map.get(completed_task)
                if ag:
                    yield f"❌ {ag.name} lỗi: {e}"

        # 3️⃣ Voting -----------------------------------------------------
        if not self.assigned_agent:
            agent_map = {a.name: a for a in self.agents}
            tally = Counter(
                ag.vote([a.name for a in self.agents], agent_map, user_prompt)
                for ag in self.agents
            )
            self.logger.log_votes(dict(tally))
            winner_name = tally.most_common(1)[0][0] if tally else None
            if winner_name:
                self.influence.record_vote(winner_name, self.round_num)

                # Giao task cho winner
                task_desc = f"Phân tích yêu cầu người dùng: {user_prompt}"
                for ag in self.agents:
                    if ag.name == winner_name:
                        task_msg = ag.assign_task(task_desc)
                        self.logger.log_task_assignment(ag.name, task_msg)
                        self.assigned_agent = ag
                        yield f"✅ Giao nhiệm vụ cho {ag.name}: {task_msg}"
                        break

                if quick_mode:
                    self.round_num += 1
                    return

        # 4️⃣ Feedback & trait update -----------------------------------
        for ag in self.agents:
            ag.reflect_on_feedback(ag == self.assigned_agent,
                                   f"Kết quả vòng {self.round_num}")

        self.round_num += 1

    # ------------------------------------------------------------------
    # LEGACY API (gom toàn bộ về list)
    # ------------------------------------------------------------------
    async def handle_input(self, user_prompt: str, quick_mode: bool = False) -> List[str]:
        return [msg async for msg in self.debate_flow(user_prompt, quick_mode)]
