# 🤖 Auto-Tuning PostgreSQL Vector Store Agent

An autonomous AI agent that monitors, analyzes, and optimizes PostgreSQL vector similarity search performance using LLM-powered decision making for production RAG workloads.

> *Built a 3-phase benchmark harness that separates cache warming from real index gains, achieving 99.7% query latency reduction through autonomous LLM-driven index selection*

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
| AI & ML | 204.18ms | 0.13ms | **99.9%** ↑ |
| Climate Change | 28.70ms | 0.11ms | **99.6%** ↑ |
| Quantum Computing | 32.34ms | 0.12ms | **99.6%** ↑ |
| Renewable Energy | 29.67ms | 0.10ms | **99.7%** ↑ |
| Space Exploration | 29.50ms | 0.10ms | **99.6%** ↑ |

**Average Improvement: 99.7%**  
**Best Performance: 99.9% faster (AI/ML query — 204ms → 0.13ms)**  
**Success Rate: 5/5 queries optimized (100%)**  
**Index Created: 1× IVFFlat (autonomous, no human intervention)**

---

## 📸 Demo

<img width="801" height="519" alt="bencmark comprasion summary" src="https://github.com/user-attachments/assets/d065130a-fc7a-4076-ad25-9223e4d44bf3" />

*Phase 1 → Phase 3 comparison: ~29ms baseline dropped to ~0.11ms after autonomous IVFFlat index creation*

<img width="795" height="506" alt="project summary" src="https://github.com/user-attachments/assets/2c5eec42-d560-43e2-8623-3aaf3bbdf0ad" />

*Complete metrics: 995 documents loaded, 1 index created, 100% success rate*

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
python scripts/clean_indexes.py

# 5. Run benchmark
python scripts/benchmark.py
```

**Expected output:**

```
🎯 AUTO-TUNING POSTGRESQL VECTOR STORE AGENT - BENCHMARK

======================================================================
PHASE 1: BASELINE PERFORMANCE TEST (No Index)
======================================================================
Query 1 (Baseline): 204.18 ms | Index Used: False
Query 2 (Baseline):  28.70 ms | Index Used: False
Query 3 (Baseline):  32.34 ms | Index Used: False
Query 4 (Baseline):  29.67 ms | Index Used: False
Query 5 (Baseline):  29.50 ms | Index Used: False

======================================================================
PHASE 2: AGENT TAKES ACTION (Triggered by Query 1)
======================================================================
👁️  OBSERVE: Execution Time: 32.16 ms | Index Used: False
🧠 REASON:  LLM Decision: create_ivfflat_index
⚡ ACT:     Creating IVFFlat index: idx_embedding_ivfflat_wikipedia
✅          Index created successfully
📈 REAL IMPROVEMENT: 99.7%
            Before: 32.16 ms → After: 0.09 ms

======================================================================
PHASE 3: POST-OPTIMIZATION VERIFICATION (All Queries)
======================================================================
Query 1 (Optimized): 0.13 ms | Index Used: True
Query 2 (Optimized): 0.11 ms | Index Used: True
Query 3 (Optimized): 0.12 ms | Index Used: True
Query 4 (Optimized): 0.10 ms | Index Used: True
Query 5 (Optimized): 0.10 ms | Index Used: True

======================================================================
📊 BENCHMARK COMPARISON SUMMARY
======================================================================
Query 1: Before: 204.18 ms -> After: 0.13 ms (Improvement: 99.9%)
Query 2: Before:  28.70 ms -> After: 0.11 ms (Improvement: 99.6%)
Query 3: Before:  32.34 ms -> After: 0.12 ms (Improvement: 99.6%)
Query 4: Before:  29.67 ms -> After: 0.10 ms (Improvement: 99.7%)
Query 5: Before:  29.50 ms -> After: 0.10 ms (Improvement: 99.6%)

✅ Benchmark complete!
```

---

## 📁 Project Structure

```
postgres-vector-agent/
├── agent/
│   ├── database.py            # PostgreSQL operations & EXPLAIN parsing
│   ├── embeddings.py          # sentence-transformers integration
│   ├── agent_core.py          # Observe-Reason-Act-Verify loop
│   ├── query_analyzer.py      # Query plan analysis
│   └── optimizer.py           # LLM-powered decision engine
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
│   ├── benchmark.py           # 3-phase performance testing
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

### 3. Production-Ready Architecture
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
ORDER BY embedding <=> '[...]'::vector
LIMIT 5;

# Extract metrics:
# - Execution Time: 204.18 ms
# - Scan Type: Sequential Scan
# - Index Used: False
```

### Reasoning Phase
```python
# LLM receives prompt:
"""
PERFORMANCE METRICS:
- Execution Time: 32.16 ms
- Scan Type: Seq Scan
- Index Used: False

QUESTION: HNSW or IVFFlat?
"""

# LLM Response:
# ACTION: create_ivfflat_index
# REASONING: Given the high latency and absence of an index,
#             IVFFlat's memory efficiency makes it suitable for
#             this scenario, balancing speed and resource consumption
# EXPECTED: 20-40x faster
```

### Action Phase
```sql
-- Agent executes autonomously:
CREATE INDEX idx_embedding_ivfflat_wikipedia
ON rag_system.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Verification Phase
```python
# Re-measure after index creation:
# Before: 32.16 ms
# After:   0.09 ms
# Improvement: 99.7%

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
