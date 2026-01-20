@echo off
echo ========================================
echo Auto-Tuning PostgreSQL Vector Store Agent
echo Windows Setup
echo ========================================
echo.

REM Check Docker Desktop
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Please install Docker Desktop for Windows.
    echo Download: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker found

REM Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not found. Installing...
    echo Please download from: https://ollama.com/download/windows
    echo After installing, run this script again.
    pause
    exit /b 1
)
echo [OK] Ollama found

REM Pull Ollama model
echo.
echo Downloading Phi-3 model (this may take a few minutes)...
ollama pull phi3:mini

REM Create virtual environment
echo.
echo Setting up Python environment...
python -m venv venv

REM Activate venv and install dependencies
echo Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Start Docker containers
echo.
echo Starting Docker containers...
cd docker
docker-compose up -d
cd ..

REM Wait for PostgreSQL
echo.
echo Waiting for PostgreSQL to be ready...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate venv: venv\Scripts\activate
echo 2. Load data: python scripts\load_data.py
echo 3. Run benchmark: python scripts\benchmark.py
echo.
echo Services:
echo - PostgreSQL: localhost:5432
echo - Prometheus: http://localhost:9090
echo - Grafana: http://localhost:3000 (admin/admin)
echo.
pause