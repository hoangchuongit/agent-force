from collections import Counter
from agents.roles.pragent import PRAgent
from agents.roles.legalagent import LegalAgent
from agents.roles.financeagent import FinanceAgent
from agents.roles.opsagent import OpsAgent
from agents.roles.criticalagent import CriticalAgent
from orchestrator.action_extractor import extract_actions_stream
from orchestrator.executor import execute_actions_stream
from orchestrator.goal_manager import GoalManager


class DeliberationOrchestrator:
    CONSENSUS_PHRASE = "tôi đồng thuận với các ý kiến trên."

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.core_agents = [
            PRAgent(llm_client),
            LegalAgent(llm_client),
            FinanceAgent(llm_client),
            OpsAgent(llm_client),
        ]
        self.critical_agent = CriticalAgent(llm_client)

        self.agents = self.core_agents + [self.critical_agent]  # Critical luôn phản biện nhưng không lead sớm

        default_goals = GoalManager.get_default_goals()
        for agent in self.agents:
            agent_key = type(agent).__name__
            agent.set_goal(default_goals.get(agent_key, ""))

    def score_agents(self, context: str):
        context_lower = context.lower()
        keyword_map = GoalManager.KEYWORD_GOALS
        scores = []
        for agent in self.core_agents:
            agent_key = type(agent).__name__
            keywords = keyword_map.get(agent_key, [])
            score = sum(1 for kw in keywords if kw in context_lower)
            scores.append((agent, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    async def run(self, context: str, max_rounds: int = 10, max_cycles: int = 5):
        goals = GoalManager.extract_goals_from_context(context)
        for agent in self.agents:
            agent_key = type(agent).__name__
            new_goal = goals.get(agent_key)
            if new_goal:
                agent.set_goal(new_goal)

        agent_scores = self.score_agents(context)
        tried_agents = set()
        cycle = 0
        soft_consensus_streak = 0

        while cycle < max_cycles:
            lead_agent = next((a for a, _ in agent_scores if type(a).__name__ not in tried_agents), None)

            # Sau 3 chu kỳ → cho phép CriticalAgent làm lead nếu chưa thử
            if not lead_agent and cycle >= 3 and type(self.critical_agent).__name__ not in tried_agents:
                lead_agent = self.critical_agent

            if not lead_agent:
                break
            tried_agents.add(type(lead_agent).__name__)
            cycle += 1

            context_with_goal = lead_agent.get_goal_context() + context
            lead_response = await lead_agent.speak(context_with_goal)
            yield {"agent": lead_agent.name, "text": lead_response["text"], "type": "lead"}
            opinions = {lead_agent.name: lead_response["text"]}

            for round_num in range(max_rounds):
                round_reviews = {}
                soft_flags = []

                merged_input = "\n".join([f"{k}:\n{v}" for k, v in opinions.items()])
                merged_prompt = (
                    "Tổng hợp nội dung sau thành một đề xuất rõ ràng, loại bỏ trùng lặp, giữ mạch logic:\n\n"
                    f"{merged_input}\n\nĐề xuất tổng hợp:"
                )
                merged_opinion = ""
                async for chunk in self.llm_client.chat_stream(merged_prompt):
                    merged_opinion += chunk

                yield {
                    "agent": "orchestrator",
                    "text": merged_opinion,
                    "type": f"merged_proposal_cycle_{cycle}_round_{round_num+1}",
                }

                for agent in self.agents:
                    try:
                        buffer = ""
                        prompt = agent.get_goal_context() + merged_opinion
                        async for chunk in agent.review_peer_outputs({"full_input": prompt}):
                            buffer += chunk
                            yield {
                                "agent": agent.name,
                                "text": chunk,
                                "type": f"stream_review_cycle_{cycle}_round_{round_num+1}",
                            }
                        review_text = buffer.strip()
                        round_reviews[agent.name] = review_text
                        yield {
                            "agent": agent.name,
                            "text": review_text,
                            "type": f"review_cycle_{cycle}_round_{round_num+1}",
                        }

                        if any(word in review_text.lower() for word in ["không đồng ý", "phản đối", "đề nghị xem xét lại"]):
                            soft_flags.append(False)
                        else:
                            soft_flags.append(True)

                    except Exception as e:
                        round_reviews[agent.name] = f"[LỖI khi phản biện]: {e}"
                        soft_flags.append(False)

                if all(soft_flags):
                    soft_consensus_streak += 1
                else:
                    soft_consensus_streak = 0

                if soft_consensus_streak >= 2:
                    yield {
                        "agent": "orchestrator",
                        "text": f"✅ Đạt soft consensus sau 2 vòng liên tiếp.",
                        "type": "soft_consensus_reached",
                    }
                    async for chunk in self._finalize(merged_opinion):
                        yield chunk
                    return

                opinions = round_reviews.copy()

            proposal_counter = Counter(opinions.values())
            most_common = proposal_counter.most_common(1)[0] if proposal_counter else None
            if most_common and most_common[1] >= 3:
                yield {
                    "agent": "orchestrator",
                    "text": f"📌 Phương án được đa số (>=3) đồng thuận sau chu kỳ {cycle}:\n{most_common[0]}",
                    "type": "final_decision",
                }
                async for chunk in self._finalize(most_common[0]):
                    yield chunk
                return
            else:
                yield {
                    "agent": "orchestrator",
                    "text": f"⚠️ Chưa đạt đồng thuận sau {max_rounds} vòng. Chuyển sang lead agent khác.",
                    "type": "no_consensus",
                }

        yield {
            "agent": "orchestrator",
            "text": "❌ Đã thử tất cả agent lead nhưng không đạt được đồng thuận.",
            "type": "final_decision_failed",
        }

        fallback_proposal = ""
        async for chunk in self.synthesize_best_effort(opinions):
            fallback_proposal += chunk
            yield {"agent": "orchestrator", "text": chunk, "type": "final_fallback_summary"}

        async for chunk in self._finalize(fallback_proposal):
            yield chunk

    async def summarize_final_proposal(self, opinions: dict) -> str:
        merged = "\n\n".join([f"{agent}:\n{content}" for agent, content in opinions.items()])
        prompt = (
            "Tình huống: Các bộ phận chuyên môn đã hoàn toàn đồng thuận sau nhiều vòng phản biện.\n"
            "Dưới đây là các ý kiến cuối cùng của từng bộ phận:\n\n"
            f"{merged}\n\n"
            "🎯 Yêu cầu:\n"
            "- Tổng hợp các ý kiến trên thành **một bản đề xuất hành động thống nhất**.\n"
            "- Ngắn gọn, rõ ràng, mang tính thực thi cao.\n"
            "- Dùng giọng văn chuyên nghiệp, nhất quán, phù hợp để gửi cho khách hàng, đối tác hoặc công bố nội bộ.\n"
            "- Tránh lặp lại, không liệt kê theo agent. Không cần nói 'PRAgent nói rằng...'\n"
            "- Nếu phù hợp, hãy viết dưới dạng thông báo chính thức hoặc email dự thảo.\n\n"
            "✍️ Bắt đầu bản đề xuất:"
        )
        yield "📄 Bản đề xuất thống nhất:\n"
        async for chunk in self.llm_client.chat_stream(prompt):
            yield chunk

    async def synthesize_best_effort(self, opinions: dict) -> str:
        merged = "\n\n".join(f"{agent}:\n{text}" for agent, text in opinions.items())
        prompt = (
            "Bối cảnh: Hệ thống AI gồm nhiều bộ phận chuyên môn (PR, Pháp lý, Tài chính, Vận hành) đã tranh luận nhiều vòng nhưng **không đạt được đồng thuận hoàn toàn**.\n"
            "Dưới đây là các ý kiến cuối cùng của từng bộ phận:\n\n"
            f"{merged}\n\n"
            "🎯 Nhiệm vụ:\n"
            "- Tổng hợp lại **các điểm chung có giá trị cao nhất**.\n"
            "- Bỏ qua các điểm tranh cãi không thể thống nhất.\n"
            "- Viết một **bản đề xuất hành động** rõ ràng, chuyên nghiệp, trung lập, có thể gửi cho cấp quản lý ra quyết định.\n"
            "- Giữ văn phong khách quan, tránh quy trách nhiệm cá nhân, tránh thuật lại ai nói gì.\n"
            "- Nếu cần, phân tách thành các phần: Tình hình – Hành động – Khuyến nghị.\n\n"
            "✍️ Bắt đầu viết bản đề xuất:"
        )
        yield "📄 Bản đề xuất tổng hợp (fallback):\n"
        async for chunk in self.llm_client.chat_stream(prompt):
            yield chunk

    async def _finalize(self, final_proposal: str):
        yield {
            "agent": "orchestrator",
            "text": final_proposal,
            "type": "final_proposal",
        }

        action_buffer = ""
        async for chunk in extract_actions_stream(self.llm_client, final_proposal):
            action_buffer += chunk
            yield {"agent": "orchestrator", "text": chunk, "type": "action_extraction"}

        try:
            actions = eval(action_buffer)
        except Exception as e:
            yield {
                "agent": "orchestrator",
                "text": f"❌ Lỗi parse actions: {e}",
                "type": "error",
            }
            return

        async for chunk in execute_actions_stream(self.llm_client, actions):
            yield {"agent": "orchestrator", "text": chunk, "type": "action_execution"}
