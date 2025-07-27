# 🧠 AgentForce – Where AI Minds Clash, Collaborate, and Evolve

## 🚀 Cách chạy local

```bash
# Bước 1: Tạo virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bước 2: Cài thư viện
pip install -r requirements.txt

# Bước 3: Khởi động server
uvicorn main:app --reload


# Bước 4: Chạy test
python -m pytest