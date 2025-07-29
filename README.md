# 🧠 AgentForce – Crisis Response Multi-Agent System

**AgentForce** is a fast, modular AI system designed to simulate how enterprises respond to crises using multiple intelligent agents (PR, Legal, Ops, Finance).  
Ideal for demos, hackathons, or integration into B2B AI workflows.

---

## 🚀 Features

- 🤖 **Multi-agent coordination** (PR, Legal, Ops, Finance)
- 🧠 **Long-term memory** via ChromaDB + summarization
- 🧩 **Role-specific response logic** per agent
- 🗣️ **Streaming WebSocket API** for real-time UI
- 📂 Ready for **production-level refactoring**

---

## 🗂️ Project Structure
```
agent-force/
├── agents/
│   ├── base.py                       # Optimized async BaseAgent with memory
│   └── roles/
│       ├── financeagent.py          # Finance-specific logic & traits
│       ├── legalagent.py            # Legal risk assessment logic
│       ├── opsagent.py              # Ops + technical issue response
│       └── pragent.py               # PR & media sentiment strategy
├── cases/
│   └── test_cases.yaml              # Example crisis situations
├── memory/
│   ├── summarizer.py                # Summarize past memory entries
│   ├── vector_memory.py             # Memory wrapper per agent
│   └── vector_store_chroma.py      # Backend: ChromaDB integration
├── orchestrator/
│   ├── action_extractor.py         # Extracts executable actions from proposal
│   ├── crisis.py                   # Coordinates multi-agent responses
│   ├── deliberation.py             # Multi-agent debate & consensus controller
│   └── executor.py                 # Executes assigned actions via agents
├── services/
│   └── llm_client.py               # OpenAI wrapper (chat & stream)
├── config.py                       # Loads .env config vars
├── run_demo.py                     # CLI runner for local testing
```

## ⚙️ Setup

1. **Clone this repo**

2. Create `.env` with your OpenAI key:
```bash
env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
TEMPERATURE=0.7
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run CLI demo:
```bash
python run_demo.py
```
Or run WebSocket API:
```
uvicorn main:app --reload --port 8001
```

## 🧪 Demo (Postman / UI)
- Connect to: ws://localhost:8001/ws
- Send a crisis scenario (e.g. "Data breach of 10,000 users")
- Agents respond in stream: PR → Legal → Finance → Ops

## 📌 Sample Use Case Scenarios
- Product malfunction impacting users
- Customer data leak
- Public boycott campaign (#BoycottCompanyX)
- Legal threats from enterprise clients
- Viral misinformation or media attack

## 🤝 Contributions
This system was designed to be modular.
You're welcome to fork, extend with new agent types, or plug into orchestration tools like LangGraph or AutoGen

## 📄 License
MIT – free to use, modify, and contribute.