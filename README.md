# 🤖 Auto-Tuning PostgreSQL Vector Store Agent

An autonomous AI agent that monitors, analyzes, and optimizes PostgreSQL vector similarity search performance using LLM-powered decision making for production RAG workloads.

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 Project Overview

This project demonstrates an **agentic coding** approach to database optimization for AI workloads. The agent autonomously:

1. **👁️ Observes** query performance using PostgreSQL `EXPLAIN ANALYZE`
2. **🧠 Reasons** about optimization strategies using local LLM (Ollama/Phi-3)
3. **⚡ Acts** by creating vector indexes (HNSW/IVFFlat) without human intervention
4. **✅ Verifies** improvements through continuous performance monitoring

Built to demonstrate expertise in **PostgreSQL internals**, **distributed systems**, and **agentic AI** for Azure Database services roles.

---

## 📊 Performance Results

**Benchmark on 995 Wikipedia articles:**

| Query | Before | After | Improvement |
|-------|--------|-------|-------------|
| AI & ML | 10.99ms | 2.07ms | **81.2%** ↑ |
| Climate Change | 2.98ms | 1.97ms | **33.9%** ↑ |
| Quantum Computing | 2.92ms | 2.06ms | **29.5%** ↑ |
| Renewable Energy | 2.99ms | 2.15ms | **28.0%** ↑ |
| Space Exploration | 2.06ms | 2.03ms | **1.5%** ↑ |

**Average Improvement: 34.8%**  
**Best Performance: 81.2% faster (AI/ML query)**  
**Success Rate: 5/5 queries optimized (100%)**

---

## 📸 Demo

![Benchmark Results](screenshots/benchmark_results.png)
*Agent achieved 81.2% optimization on first query through autonomous IVFFlat index selection*

![Agent Decision](screenshots/agent_decision.png)
*LLM-powered reasoning: Observe → Reason → Act → Verify loop in action*

![Project Summary](screenshots/project_summary.png)
*Complete metrics: 995 documents, 28 total optimizations, 100% success rate*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query Request                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼─────┐
                    │  OBSERVE │ ← PostgreSQL EXPLAIN ANALYZE
                    └────┬─────┘   (Execution time, scan type, index usage)
                         │
                    ┌────▼─────┐
                    │  REASON  │ ← Ollama (Phi-3 Mini LLM)
                    └────┬─────┘   (HNSW vs IVFFlat decision)
                         │
                    ┌────▼─────┐
                    │   ACT    │ ← CREATE INDEX (autonomous)
                    └────┬─────┘   (IVFFlat/HNSW with params)
                         │
                    ┌────▼─────┐
                    │  VERIFY  │ ← Re-measure & log metrics
                    └──────────┘   (Prometheus + Grafana)
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | PostgreSQL 16 + pgvector | Vector storage & similarity search |
| **LLM** | Ollama (Phi-3 Mini) | Autonomous optimization decisions |
| **Embeddings** | sentence-transformers | Text-to-vector (384-dim) |
| **Monitoring** | Prometheus + Grafana | Real-time performance tracking |
| **Language** | Python 3.10+ | Agent orchestration |
| **Infrastructure** | Docker Compose | Multi-service deployment |
| **Connection Pool** | PgBouncer | 1000+ concurrent connections |
| **Replication** | PostgreSQL Streaming | Master-slave failover ready |

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.10+
- 8GB RAM minimum
- 10GB disk space

### Installation

```bash
# 1. Clone repository
git clone https://github.com/merenceleby/postgres-vector-agent
cd postgres-vector-agent

# 2. Run setup
setup-windows.bat  # Windows
# OR
./scripts/setup.sh  # Linux/Mac

# 3. Activate Python environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# 4. Load sample data
python scripts/load_data.py --num-docs 1000

# 5. Run benchmark
python scripts/benchmark.py
```

**Expected output:**
```
🎯 AUTO-TUNING POSTGRESQL VECTOR STORE AGENT - BENCHMARK

Query 1/5: 'artificial intelligence and machine learning'
📊 Execution Time: 10.99 ms (Before)
🧠 LLM Decision: create_ivfflat_index
⚡ Creating IVFFlat index...
✅ Index created successfully
📈 IMPROVEMENT: 81.2%
   Before: 10.99 ms → After: 2.07 ms

======================================================================
📊 BENCHMARK SUMMARY
Average Improvement: 34.8%
```

---

## 📁 Project Structure

```
postgres-vector-agent/
├── agent/
│   ├── database.py           # PostgreSQL operations & EXPLAIN parsing
│   ├── embeddings.py         # sentence-transformers integration
│   ├── agent_core.py         # Observe-Reason-Act-Verify loop
│   ├── query_analyzer.py      # Query plan analysis
│   └── optimizer.py          # LLM-powered decision engine
├── docker/
│   ├── docker-compose.yml     # Multi-service orchestration
│   ├── init.sql               # Schema + partitioning + extensions
│   └── postgresql.conf        # Tuned for vector workloads
├── monitoring/
│   ├── prometheus.yml         # Metrics collection config
│   └── grafana-dashboard.json # Visual metrics tracking
├── scripts/
│   ├── setup.sh               # Linux/Mac automated setup
│   ├── load_data.py           # Wikipedia data loader
│   ├── benchmark.py           # Performance testing
│   ├── clean_indexes.py       # Reset for testing
│   └── summary.py             # Project metrics display
├── requirements.txt           # Python dependencies
├── setup-windows.bat          # Automated Windows setup
└── README.md                  # Project documentation

```

---

## 🎓 Key Features

### 1. Autonomous Query Optimization
- Parses PostgreSQL `EXPLAIN ANALYZE` JSON output
- Detects sequential scans, missing indexes, and bottlenecks
- No manual intervention required

### 2. LLM-Powered Decision Making
- Uses Phi-3 (3.8B parameters) running locally via Ollama
- Analyzes query patterns and dataset characteristics
- Chooses between HNSW (speed) vs IVFFlat (memory)
- Low temperature (0.3) for consistent technical decisions

### 3. Production-Grade Infrastructure
- Multi-tenant partitioning with row-level security
- PgBouncer connection pooling (1000+ concurrent)
- Master-slave replication for high availability
- Prometheus + Grafana for observability

### 4. Vector Search Optimization
- pgvector extension for cosine similarity
- HNSW indexes (m=16, ef_construction=64)
- IVFFlat indexes (lists=100)
- 384-dimensional embeddings

---

## 📊 How It Works

### Observation Phase
```python
# Execute EXPLAIN ANALYZE
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT content FROM documents
ORDER BY embedding <-> '[...]'::vector
LIMIT 5;

# Extract metrics:
# - Execution Time: 10.99 ms
# - Scan Type: Sequential Scan
# - Index Used: False
```

### Reasoning Phase
```python
# LLM receives prompt:
"""
PERFORMANCE METRICS:
- Execution Time: 10.99 ms
- Scan Type: Seq Scan
- Index Used: False

QUESTION: HNSW or IVFFlat?
"""

# LLM Response:
# ACTION: create_ivfflat_index
# REASONING: Memory efficiency for large dataset
# EXPECTED: 20-40x faster
```

### Action Phase
```sql
-- Agent executes:
CREATE INDEX idx_embedding_ivfflat_wikipedia
ON rag_system.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Verification Phase
```python
# Re-measure:
# Before: 10.99 ms
# After:  2.07 ms
# Improvement: 81.2%

# Log to database
INSERT INTO rag_system.agent_actions...
```

---

## 📊 Monitoring

### Grafana Dashboard
Access: `http://localhost:3000` (admin/admin)

**Metrics tracked:**
- Query execution time trends
- Index hit/miss ratio
- Agent optimization frequency
- Database connection pool utilization

### Database Stats
```sql
-- View query performance
SELECT * FROM rag_system.query_metrics
ORDER BY timestamp DESC LIMIT 10;

-- See agent decisions
SELECT action_type, reasoning, success
FROM rag_system.agent_actions
ORDER BY timestamp DESC;

-- Check indexes
SELECT * FROM rag_system.index_registry;
```

### Project Summary
```bash
python scripts/summary.py
```

---

## 🧪 Testing

### Run Benchmark
```bash
python scripts/benchmark.py
```

### Clean State
```bash
python scripts/clean_indexes.py
```

### Load Custom Data
```python
from agent.database import DatabaseManager
from agent.embeddings import EmbeddingGenerator

db = DatabaseManager()
embedder = EmbeddingGenerator()

documents = [{
    'tenant_id': 'my_app',
    'content': 'Your text',
    'embedding': embedder.encode_query('Your text'),
    'metadata': {}
}]

db.insert_documents(documents)
```

---

## 🎯 Use Cases

1. **RAG Pipeline Optimization** - Auto-tune vector search for LLM apps
2. **Multi-Tenant SaaS** - Per-tenant database optimization
3. **Production Monitoring** - Detect/fix slow queries autonomously
4. **Index Strategy Testing** - Compare HNSW vs IVFFlat
5. **Database Education** - Learn PostgreSQL optimization

---


## 📝 License

MIT License - see [LICENSE](LICENSE) file

---


## 👨‍💻 Author

**[Muhammed Eren Çelebi]**  
Building autonomous database optimization for AI workloads

📧 [E-mail](mailto:muhammederencelebii@gmail.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/merencelebi/)  
🐙 [GitHub](https://github.com/merenceleby)

---
