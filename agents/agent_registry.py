from agents.roles.devduy import create_devduy
from agents.roles.devtrang import create_devtrang
from agents.roles.qakhanh import create_qakhanh
from agents.roles.pmphuong import create_pmphuong
from agents.roles.bahieu import create_bahieu
from agents.roles.csanh import create_csanh


class AgentRegistry:
    def __init__(self, llm_client, vector_store):
        self.llm = llm_client
        self.vector_store = vector_store
        self.agents = self._register_all()

    def _register_all(self):
        return {
            "Duy": create_devduy(self.llm, self.vector_store),
            "Trang": create_devtrang(self.llm, self.vector_store),
            "Khanh": create_qakhanh(self.llm, self.vector_store),
            "Phuong": create_pmphuong(self.llm, self.vector_store),
            "Hieu": create_bahieu(self.llm, self.vector_store),
            "Anh": create_csanh(self.llm, self.vector_store),
        }

    def all(self):
        return list(self.agents.values())

    def get(self, name):
        return self.agents.get(name)


def load_all_agents(llm_client):
    from memory.vector_memory import get_default_vector_store
    vector_store = get_default_vector_store()
    return AgentRegistry(llm_client, vector_store).all()