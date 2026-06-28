@echo off
REM AgroEdge AI — start backend + frontend together (Windows).
REM Assumes you've already run setup once (see README.md):
REM   backend:  python -m venv venv  &&  venv\Scripts\activate  &&  pip install -r requirements.txt
REM   frontend: npm install

setlocal
cd /d "%~dp0"

echo AgroEdge AI - starting services
echo --------------------------------

REM 1. Check Ollama is reachable
curl -s -o NUL -m 3 http://localhost:11434
if errorlevel 1 (
  echo Ollama doesn't seem to be running at http://localhost:11434.
  echo Start it first ^(open the Ollama app, or run "ollama serve"^), then re-run this script.
  exit /b 1
)
echo [ok] Ollama is reachable.

REM 2. Check backend venv exists
if not exist "backend\venv" (
  echo [!] backend\venv not found. Run setup first:
  echo     cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
  exit /b 1
)

REM Check the embedding model has been downloaded at least once. Without
REM this, the backend fails on every chat request with "Cannot send a
REM request, as the client has been closed" when run offline.
dir /b "%USERPROFILE%\.cache\huggingface\hub\*all-MiniLM-L6-v2*" >nul 2>&1
if errorlevel 1 (
  echo [!] all-MiniLM-L6-v2 doesn't appear to be cached yet.
  echo     Run this once, with internet connected, before going offline:
  echo     cd backend ^&^& venv\Scripts\activate ^&^& python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
  echo     Continuing anyway in case the cache is in a non-default location...
)

REM 3. Start backend in its own window
echo Starting backend (FastAPI) on :8000 ...
start "AgroEdge Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --port 8000"

REM 4. Check frontend deps exist
if not exist "frontend\node_modules" (
  echo [!] frontend\node_modules not found. Run setup first:
  echo     cd frontend ^&^& npm install
  exit /b 1
)

REM 5. Start frontend in its own window
echo Starting frontend (Next.js) on :3000 ...
start "AgroEdge Frontend" cmd /k "cd frontend && npm run dev"

echo --------------------------------
echo Backend:  http://localhost:8000  (see "AgroEdge Backend" window)
echo Frontend: http://localhost:3000  (see "AgroEdge Frontend" window)
echo.
echo Run stop.bat to close both, or just close their windows.

endlocal