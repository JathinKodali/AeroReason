#!/bin/bash
# ═══════════════════════════════════════════════
#  AeroReason — Stop all services
# ═══════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}Stopping AeroReason...${NC}"

pkill -f "uvicorn api_server" 2>/dev/null && echo -e "  ${GREEN}✓${NC} API server stopped" || echo -e "  ${RED}—${NC} API server was not running"
pkill -f "vite" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Frontend stopped" || echo -e "  ${RED}—${NC} Frontend was not running"

echo -e "${GREEN}Done.${NC}"
