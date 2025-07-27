def should_respond(agent, context: str) -> bool:
    """
    Agent quyết định có nên phản hồi dựa trên:
    - Trait (extraversion, agreeableness...)
    - Emotion hiện tại
    - LLM phân tích cuối nếu cần
    """
    emotion = agent.emotion.current_emotion()
    traits = agent.traits
    extroversion = traits.get("extraversion", 0.5)
    agreeableness = traits.get("agreeableness", 0.5)

    context_lower = context.lower()

    # 🔥 Logic nhanh nếu cảm xúc mạnh hoặc tính cách nổi bật
    if emotion in ["giận dữ", "bực tức", "cay cú"]:
        return True
    if extroversion > 0.8 and "tranh luận" in context_lower:
        return True
    if agreeableness < 0.3 and any(kw in context_lower for kw in ["bị phản bác", "chỉ trích"]):
        return True

    # ❓ Nếu chưa rõ — gọi LLM quyết định
    prompt = (
        f"Agent: {agent.name} – Role: {agent.role}\n"
        f"Tính cách: {traits}\n"
        f"Cảm xúc hiện tại: {emotion}\n"
        f"Context: {context}\n"
        "Dựa trên tính cách, cảm xúc và động lực hiện tại, agent này có nên phát biểu không? "
        "Chỉ trả lời 'yes' hoặc 'no'."
    )
    response = agent.llm.chat(prompt).strip().lower()
    return "yes" in response
