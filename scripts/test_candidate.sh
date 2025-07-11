#!/bin/bash
# Quick test script for candidate processing

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Recruitment Operations Test ===${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check environment variables
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env with:"
    echo "  ANTHROPIC_API_KEY=your_key"
    echo "  CATS_API_KEY=your_key"
    exit 1
fi

# Default test candidate
CANDIDATE_ID=${1:-409281807}

echo -e "${GREEN}Testing with candidate ID: $CANDIDATE_ID${NC}"

# Run the processing
python3 scripts/process_candidate.py $CANDIDATE_ID

# Check the notes
echo -e "\n${GREEN}Checking saved notes...${NC}"
python3 scripts/check_notes.py

# Show log location
echo -e "\n${YELLOW}Logs saved to: logs/recruitment_ops_$(date +%Y%m%d).log${NC}"