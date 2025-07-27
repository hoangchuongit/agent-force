from agents.base_agent import BaseAgent
from services.openai_client import OpenAIClient
from memory.vector_store_chroma import ChromaVectorStore

def create_qakhanh(llm, vector_store):
    traits = {
        "logic": 0.9,
        "empathy": 0.2,
        "openness": 0.5,
        "extraversion": 0.4,
        "agreeableness": 0.6,
        "neuroticism": 0.3
    }

    return BaseAgent(
        name="QA Khanh",
        role="Chuyên viên kiểm thử logic",
        traits=traits,
        llm_client=llm,
        vector_store=vector_store
    )
