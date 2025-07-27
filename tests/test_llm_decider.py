# tests/test_llm_decider.py
from agents.base_agent import BaseAgent
from memory.vector_store_chroma import ChromaVectorStore
from services.openai_client import OpenAIClient
from agents.utils.llm_decider import should_respond


class MockEmotion:
    def __init__(self, emotion):
        self._emotion = emotion
    def current_emotion(self):
        return self._emotion


class MockLLM:
    def chat(self, prompt):
        print(f"[Mock LLM received prompt]: {prompt[:80]}...")
        return "yes" if "phát biểu" in prompt else "no"


class DummyMemory:
    def store(self, x): pass
    def retrieve(self, x): return ""


def create_mock_agent(name, emotion, traits):
    agent = BaseAgent(
        name=name,
        role="Dev",
        traits=traits,
        llm_client=MockLLM(),
        vector_store=ChromaVectorStore()
    )
    agent.emotion = MockEmotion(emotion)
    agent.memory = DummyMemory()
    return agent


def test_should_respond_angry():
    agent = create_mock_agent("TestBot1", emotion="giận dữ", traits={"extraversion": 0.2})
    context = "Không ai chịu nghe ý kiến của tôi!"
    assert should_respond(agent, context) == True


def test_should_respond_extrovert():
    agent = create_mock_agent("TestBot2", emotion="bình tĩnh", traits={"extraversion": 0.9})
    context = "Chúng ta đang tranh luận rất gay gắt."
    assert should_respond(agent, context) == True


def test_should_respond_agreeableness_low():
    agent = create_mock_agent("TestBot3", emotion="bình tĩnh", traits={"agreeableness": 0.1})
    context = "Câu trả lời của bạn bị phản bác bởi người khác."
    assert should_respond(agent, context) == True


def test_should_respond_llm_fallback():
    agent = create_mock_agent("TestBot4", emotion="bình tĩnh", traits={"extraversion": 0.4})
