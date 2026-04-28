#!/bin/bash
# ═══════════════════════════════════════════════
#  AeroReason — One-click launcher
#  Starts the FastAPI backend + React frontend
# ═══════════════════════════════════════════════

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_DIR/venv"
FRONTEND="$PROJECT_DIR/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║       AeroReason  —  Launcher        ║"
echo "  ║   Predictive Maintenance Framework   ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── Cleanup on exit ──────────────────────────
cleanup() {
    echo -e "\n${CYAN}Shutting down...${NC}"
    kill $API_PID 2>/dev/null
    kill $FE_PID 2>/dev/null
    wait $API_PID 2>/dev/null
    wait $FE_PID 2>/dev/null
    echo -e "${GREEN}All processes stopped.${NC}"
}
trap cleanup EXIT INT TERM

# ── Check prerequisites ──────────────────────
if [ ! -d "$VENV" ]; then
    echo -e "${RED}Error: Python venv not found at $VENV${NC}"
    echo "  Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if [ ! -d "$FRONTEND/node_modules" ]; then
    echo -e "${CYAN}Installing frontend dependencies...${NC}"
    cd "$FRONTEND" && npm install
fi

# ── Check Ollama service ─────────────────────
echo -e "${CYAN}Checking Ollama service...${NC}"
if pgrep -x "ollama" > /dev/null 2>&1; then
    # Process is running, now verify the API is reachable
    if curl -s --max-time 3 http://localhost:11434/ > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Ollama is running and API is reachable${NC}"
    else
        echo -e "${RED}  ⚠ Ollama process found but API is not responding on port 11434${NC}"
        echo -e "    Try restarting: ${BOLD}ollama serve${NC}"
    fi
else
    echo -e "${RED}  ⚠ Ollama is not running${NC}"
    echo -e "    Start it with: ${BOLD}ollama serve${NC}"
    echo -e "    AI-powered insights will be unavailable without Ollama."
fi
echo ""

# ── Start API server ─────────────────────────
echo -e "${CYAN}[1/2]${NC} Starting FastAPI backend on ${BOLD}http://localhost:8000${NC}"
cd "$PROJECT_DIR"
TF_ENABLE_ONEDNN_OPTS=0 "$VENV/bin/python" -m uvicorn api_server:app \
    --port 8000 --host 0.0.0.0 --log-level info &
API_PID=$!
sleep 2

# Quick health check
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}API server failed to start. Check logs above.${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ API server running (PID $API_PID)${NC}"

# ── Start React frontend ─────────────────────
echo -e "${CYAN}[2/2]${NC} Starting React frontend on ${BOLD}http://localhost:5173${NC}"
cd "$FRONTEND"
npx vite --host &
FE_PID=$!
sleep 2

if ! kill -0 $FE_PID 2>/dev/null; then
    echo -e "${RED}Frontend failed to start. Check logs above.${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Frontend running (PID $FE_PID)${NC}"

# ── Ready ─────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}  ✅ AeroReason is ready!${NC}"
echo -e "  ${CYAN}→${NC} Open ${BOLD}http://localhost:5173${NC} in your browser"
echo -e "  ${CYAN}→${NC} API docs at ${BOLD}http://localhost:8000/docs${NC}"
echo -e "  ${CYAN}→${NC} Press ${BOLD}Ctrl+C${NC} to stop everything"
echo ""

# Keep alive
wait
