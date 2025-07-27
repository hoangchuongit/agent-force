from agents.base_agent import BaseAgent

def create_devtrang(llm, vector_store):
    traits = {
        "logic": 0.6,
        "empathy": 0.2,
        "openness": 0.8,
        "extraversion": 0.85,
        "agreeableness": 0.3,
        "neuroticism": 0.7
    }

    return BaseAgent(
        name="Dev Trang",
        role="Lập trình viên hướng cạnh tranh",
        traits=traits,
        llm_client=llm,
        vector_store=vector_store
    )
