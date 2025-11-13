#!/bin/bash

# Zero Trust Security Framework - Deployment Verification Script
# This script verifies that all components are properly configured and ready for deployment

echo "========================================="
echo "Zero Trust Security Framework"
echo "Deployment Verification Script"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
        return 1
    fi
}

# Function to check if a directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
        return 1
    fi
}

# Function to check if a command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 installed"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $2 not found"
        ((WARNINGS++))
        return 1
    fi
}

# Function to check if a service is running
check_service() {
    if pgrep -x "$1" > /dev/null; then
        echo -e "${GREEN}✓${NC} $2 is running"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $2 is not running"
        ((WARNINGS++))
        return 1
    fi
}

echo "1. Checking Prerequisites..."
echo "----------------------------"
check_command "node" "Node.js"
check_command "npm" "npm"
check_command "python3" "Python 3"
check_command "pip3" "pip3"
check_command "redis-server" "Redis"
check_command "rabbitmq-server" "RabbitMQ"
echo ""

echo "2. Checking Project Structure..."
echo "--------------------------------"
check_dir "backend" "Backend directory"
check_dir "frontend" "Frontend directory"
check_dir "backend/app" "Backend app directory"
check_dir "frontend/src" "Frontend src directory"
check_dir ".kiro/specs" "Specification directory"
echo ""

echo "3. Checking Backend Files..."
echo "----------------------------"
check_file "backend/requirements.txt" "Backend requirements.txt"
check_file "backend/run.py" "Backend run.py"
check_file "backend/.env.example" ".env.example"
check_file "backend/firebase-credentials.json.example" "Firebase credentials example"
check_file "backend/Dockerfile" "Dockerfile"
check_file "backend/app.yaml" "Google App Engine config"
check_file "backend/render.yaml" "Render config"
check_file "backend/firestore.rules" "Firestore rules"
check_file "backend/firestore.indexes.json" "Firestore indexes"
echo ""

echo "4. Checking Backend Services..."
echo "-------------------------------"
check_file "backend/app/services/auth_service.py" "Auth service"
check_file "backend/app/services/policy_engine.py" "Policy engine"
check_file "backend/app/services/behavioral_biometrics.py" "Behavioral biometrics"
check_file "backend/app/services/threat_predictor.py" "Threat predictor"
check_file "backend/app/services/contextual_intelligence.py" "Contextual intelligence"
check_file "backend/app/services/security_assistant.py" "Security assistant"
check_file "backend/app/services/blockchain_service.py" "Blockchain service"
check_file "backend/app/services/cache_service.py" "Cache service"
echo ""

echo "5. Checking Backend Routes..."
echo "-----------------------------"
check_file "backend/app/routes/auth_routes.py" "Auth routes"
check_file "backend/app/routes/access_routes.py" "Access routes"
check_file "backend/app/routes/admin_routes.py" "Admin routes"
check_file "backend/app/routes/behavioral_routes.py" "Behavioral routes"
check_file "backend/app/routes/threat_routes.py" "Threat routes"
check_file "backend/app/routes/context_routes.py" "Context routes"
check_file "backend/app/routes/assistant_routes.py" "Assistant routes"
echo ""

echo "6. Checking Frontend Files..."
echo "-----------------------------"
check_file "frontend/package.json" "Frontend package.json"
check_file "frontend/.env.example" "Frontend .env.example"
check_file "frontend/src/App.js" "App.js"
check_file "frontend/src/index.js" "index.js"
check_file "frontend/tailwind.config.js" "Tailwind config"
echo ""

echo "7. Checking Frontend Components..."
echo "----------------------------------"
check_file "frontend/src/components/auth/Login.jsx" "Login component"
check_file "frontend/src/components/dashboards/AdminDashboard.jsx" "Admin dashboard"
check_file "frontend/src/components/behavioral/BehavioralTracker.jsx" "Behavioral tracker"
check_file "frontend/src/components/ai/SecurityAssistant.jsx" "Security assistant"
check_file "frontend/src/components/ui/ThemeToggle.jsx" "Theme toggle"
echo ""

echo "8. Checking Documentation..."
echo "----------------------------"
check_file "README.md" "Main README"
check_file "PROJECT_COMPLETION_SUMMARY.md" "Project completion summary"
check_file "FINAL_STATUS.md" "Final status document"
check_file "backend/README.md" "Backend README"
check_file "backend/API_DOCUMENTATION.md" "API documentation"
check_file "backend/DEPLOYMENT_GUIDE.md" "Deployment guide"
echo ""

echo "9. Checking Configuration Files..."
echo "----------------------------------"
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC} Backend .env exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Backend .env not found (copy from .env.example)"
    ((WARNINGS++))
fi

if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓${NC} Frontend .env exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Frontend .env not found (copy from .env.example)"
    ((WARNINGS++))
fi

if [ -f "backend/firebase-credentials.json" ]; then
    echo -e "${GREEN}✓${NC} Firebase credentials exist"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Firebase credentials not found"
    ((WARNINGS++))
fi
echo ""

echo "10. Checking Dependencies..."
echo "---------------------------"
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Python virtual environment exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Python virtual environment not found"
    ((WARNINGS++))
fi

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node modules installed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Node modules not installed (run npm install)"
    ((WARNINGS++))
fi
echo ""

echo "11. Checking Services (Optional)..."
echo "-----------------------------------"
check_service "redis-server" "Redis"
check_service "rabbitmq-server" "RabbitMQ"
echo ""

echo "========================================="
echo "Verification Summary"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env files (backend and frontend)"
    echo "2. Add Firebase credentials (backend/firebase-credentials.json)"
    echo "3. Install dependencies:"
    echo "   - Backend: cd backend && pip install -r requirements.txt"
    echo "   - Frontend: cd frontend && npm install"
    echo "4. Start services:"
    echo "   - Redis: redis-server"
    echo "   - RabbitMQ: rabbitmq-server"
    echo "   - Celery: cd backend && ./start_celery.sh"
    echo "   - Backend: cd backend && python run.py"
    echo "   - Frontend: cd frontend && npm start"
    echo ""
    echo "For detailed instructions, see:"
    echo "- README.md"
    echo "- backend/DEPLOYMENT_GUIDE.md"
    echo "- PROJECT_COMPLETION_SUMMARY.md"
    exit 0
else
    echo -e "${RED}✗ Some critical checks failed!${NC}"
    echo "Please review the errors above and fix them before deployment."
    exit 1
fi
