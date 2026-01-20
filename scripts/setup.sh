#!/bin/bash

echo "🚀 Setting up Auto-Tuning PostgreSQL Vector Store Agent"
echo "=========================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "✅ Ollama found"

# Pull Ollama model
echo "📥 Pulling Phi-3 model (this may take a few minutes)..."
ollama pull phi3:mini

echo "✅ Model downloaded"

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python environment ready"

# Start Docker containers
echo "🐳 Starting Docker containers..."
cd docker
docker-compose up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Load data: python scripts/load_data.py"
echo "3. Run benchmark: python scripts/benchmark.py"
echo ""
echo "Services:"
echo "- PostgreSQL: localhost:5432"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo ""