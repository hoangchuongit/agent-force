from collections import Counter
from agents.roles.pragent import PRAgent
from agents.roles.legalagent import LegalAgent
from agents.roles.financeagent import FinanceAgent
from agents.roles.opsagent import OpsAgent

class DeliberationOrchestrator:
    CONSENSUS_PHRASE = "tôi đồng thuận với các ý kiến trên."

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.agents = [
            PRAgent(llm_client),
            LegalAgent(llm_client),
            FinanceAgent(llm_client),
            OpsAgent(llm_client)
        ]

    def score_agents(self, context: str):
        context_lower = context.lower()
        keyword_map = {
            "PRAgent": ["truyền thông", "khách hàng", "dư luận", "báo chí", "phản hồi", "tuyên bố", "xin lỗi"],
            "LegalAgent": ["pháp lý", "vi phạm", "luật", "quy định", "trách nhiệm", "kiện tụng", "tuân thủ"],
            "FinanceAgent": ["tài chính", "tiền", "thiệt hại", "bồi thường", "báo cáo", "chi phí", "lỗ", "doanh thu"],
            "OpsAgent": ["hệ thống", "vận hành", "sự cố", "hạ tầng", "rò rỉ", "server", "kỹ thuật", "khắc phục"]
        }
        scores = []
        for agent in self.agents:
            agent_key = type(agent).__name__
            keywords = keyword_map.get(agent_key, [])
            score = sum(1 for kw in keywords if kw in context_lower)
            scores.append((agent, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    async def run(self, context: str, max_rounds: int = 5, max_cycles: int = 2):
        agent_scores = self.score_agents(context)
        tried_agents = set()
        cycle = 0

        while cycle < max_cycles:
            lead_agent = next((a for a, _ in agent_scores if a.name not in tried_agents), None)
            if not lead_agent:
                break
            tried_agents.add(lead_agent.name)
            cycle += 1

            lead_response = await lead_agent.speak(context)
            yield {
                "agent": lead_agent.name,
                "text": lead_response["text"],
                "type": "lead"
            }

            opinions = {lead_agent.name: lead_response["text"]}

            for round_num in range(max_rounds):
                round_reviews = {}
                round_result = []

                for agent in self.agents:
                    try:
                        buffer = ""
                        async for chunk in agent.review_peer_outputs(opinions):
                            buffer += chunk
                            yield {
                                "agent": agent.name,
                                "text": chunk,
                                "type": f"stream_review_cycle_{cycle}_round_{round_num+1}"
                            }
                        review_text = buffer.strip()
                        round_reviews[agent.name] = review_text
                        round_result.append({
                            "agent": agent.name,
                            "text": review_text,
                            "type": f"review_cycle_{cycle}_round_{round_num+1}"
                        })
                    except Exception as e:
                        round_result.append({
                            "agent": agent.name,
                            "text": f"[LỖI khi phản biện]: {e}",
                            "type": f"review_error_cycle_{cycle}_round_{round_num+1}"
                        })

                for r in round_result:
                    yield r

                # ✅ Kết thúc sớm nếu tất cả phản hồi là câu đồng thuận chuẩn hóa
                normalized = [text.lower().strip() for text in round_reviews.values()]
                if all(t == self.CONSENSUS_PHRASE for t in normalized):
                    yield {
                        "agent": "orchestrator",
                        "text": f"✅ Tất cả agent đồng thuận sớm ở vòng {round_num+1} (chu kỳ {cycle}).",
                        "type": "final_decision"
                    }
                    
                    # 👉 Gọi thêm bước tổng hợp từ các phản hồi trước đó
                    async for chunk in self.summarize_final_proposal(opinions):
                        yield {
                            "agent": "orchestrator",
                            "text": chunk,
                            "type": "final_proposal"
                        }
                    return

                opinions = round_reviews.copy()

            # ✅ Nếu hết vòng mà vẫn chưa đồng thuận hoàn toàn → tìm đa số
            proposal_counter = Counter(opinions.values())
            most_common = proposal_counter.most_common(1)[0] if proposal_counter else None

            if most_common and most_common[1] >= 3:
                yield {
                    "agent": "orchestrator",
                    "text": f"📌 Phương án được đa số (>=3) đồng thuận sau chu kỳ {cycle}:\n{most_common[0]}",
                    "type": "final_decision"
                }
                return
            else:
                yield {
                    "agent": "orchestrator",
                    "text": f"⚠️ Chưa đạt đồng thuận sau {max_rounds} vòng (chu kỳ {cycle}). Chuyển lead agent khác để tiếp tục tranh luận.",
                    "type": "no_consensus"
                }

        yield {
            "agent": "orchestrator",
            "text": "❌ Đã thử tất cả agent lead nhưng không đạt được đồng thuận.",
            "type": "final_decision_failed"
        }
        
        # Gọi synthesize fallback nếu có opinions
        if opinions:
            async for chunk in self.synthesize_best_effort(opinions):
                yield {
                    "agent": "orchestrator",
                    "text": chunk,
                    "type": "final_fallback_summary"
                }
        
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

        # Header mở đầu
        yield "📄 Bản đề xuất thống nhất:\n"
        # Stream nội dung từ LLM
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
