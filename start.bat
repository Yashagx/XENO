@echo off
echo ============================================
echo  XENO ORACLE - Starting All Services
echo ============================================

echo.
echo [1/4] Starting Docker (PostgreSQL + Redis)...
docker-compose up -d
timeout /t 5

echo.
echo [2/4] Starting Backend API (port 8000)...
start "XENO Backend" cmd /k "cd backend && .venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3

echo.
echo [3/4] Starting Channel Service (port 8001)...
start "XENO Channel Service" cmd /k "cd channel-service && pip install -r requirements.txt -q && python main.py"
timeout /t 2

echo.
echo [4/4] Starting Frontend (port 3000)...
start "XENO Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo  XENO ORACLE is starting up!
echo  Frontend:  http://localhost:3000
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo  Channel:   http://localhost:8001
echo ============================================
echo.
pause
