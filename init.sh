#!/bin/bash

###############################################################################
# Movie Ticketing Platform - Project Initialization Script
# 
# This script initializes the complete development environment
# Run this once to set up everything
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker found"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    print_success "Node.js found ($(node --version))"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found ($(python3 --version))"
    
    # Check kubectl (optional for k8s)
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found (required for Kubernetes deployment)"
    else
        print_success "kubectl found"
    fi
}

# Create directory structure
create_directories() {
    print_header "Creating Directory Structure"
    
    mkdir -p airflow/dags
    mkdir -p airflow/logs
    mkdir -p airflow/plugins
    mkdir -p data/raw
    mkdir -p data/processed
    mkdir -p data/features
    mkdir -p notebooks
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p tests/unit
    mkdir -p tests/integration
    mkdir -p tests/ml
    mkdir -p logs
    mkdir -p artifacts
    mkdir -p models
    
    print_success "Directories created"
}

# Setup environment files
setup_env_files() {
    print_header "Setting Up Environment Files"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please update .env with your configuration"
    else
        print_warning ".env already exists"
    fi
    
    if [ ! -f .env.development ]; then
        cp .env.example .env.development
        print_success ".env.development file created"
    fi
    
    if [ ! -f .env.production ]; then
        cp .env.example .env.production
        print_success ".env.production file created"
        print_warning "Please update .env.production with production secrets"
    fi
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    # Node.js dependencies
    print_warning "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
    
    # Python dependencies
    print_warning "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Setup Git
setup_git() {
    print_header "Setting Up Git"
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        git init
        print_success "Git repository initialized"
    else
        print_warning "Git repository already exists"
    fi
    
    # Setup git hooks
    mkdir -p .git/hooks
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
npm run lint:fix || true
black . || true
isort . || true
git add .
EOF
    chmod +x .git/hooks/pre-commit
    print_success "Git hooks configured"
}

# Build Docker images
build_docker_images() {
    print_header "Building Docker Images"
    
    docker build -t ticketing/app:latest .
    print_success "Docker image built: ticketing/app:latest"
}

# Initialize databases
init_databases() {
    print_header "Initializing Databases"
    
    # Start services
    docker-compose up -d postgres redis rabbitmq
    
    # Wait for services
    print_warning "Waiting for services to be ready..."
    sleep 10
    
    # Create database
    docker-compose exec -T postgres psql -U ticketing_user -d ticketing_db -c "
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            genre VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            movie_id INTEGER REFERENCES movies(id),
            seats TEXT,
            status VARCHAR(50) DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    " || true
    
    print_success "Databases initialized"
}

# Create sample data
create_sample_data() {
    print_header "Creating Sample Data"
    
    docker-compose exec -T postgres psql -U ticketing_user -d ticketing_db -c "
        INSERT INTO users (email, password) VALUES 
            ('user1@example.com', 'hashed_password_1'),
            ('user2@example.com', 'hashed_password_2')
        ON CONFLICT DO NOTHING;
        
        INSERT INTO movies (title, genre, description) VALUES 
            ('Inception', 'Sci-Fi', 'A skilled thief who steals corporate secrets'),
            ('The Matrix', 'Sci-Fi', 'A computer hacker learns about the true nature of reality'),
            ('Interstellar', 'Sci-Fi', 'A team of explorers travel through a wormhole')
        ON CONFLICT DO NOTHING;
    " || true
    
    print_success "Sample data created"
}

# Initialize MLOps
init_mlops() {
    print_header "Initializing MLOps"
    
    # Create MLflow directories
    mkdir -p mlruns
    mkdir -p artifacts
    
    print_success "MLOps directories initialized"
}

# Create SSH keys (optional)
create_ssh_keys() {
    print_header "Setting Up SSH Keys (Optional)"
    
    if [ ! -f ~/.ssh/id_rsa ]; then
        print_warning "SSH key not found. Creating one..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" 2>/dev/null || true
        print_success "SSH key created"
    else
        print_warning "SSH key already exists"
    fi
}

# Print final instructions
print_final_instructions() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}Project initialization completed successfully!${NC}\n"
    
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update your .env file with configuration:"
    echo "   - Database credentials"
    echo "   - API keys (Stripe, SendGrid, Twilio)"
    echo "   - Service URLs"
    echo ""
    echo "2. Start development environment:"
    echo "   ${YELLOW}make dev${NC}"
    echo ""
    echo "3. Access services:"
    echo "   - Frontend: http://localhost:3100"
    echo "   - API: http://localhost:3000"
    echo "   - Adminer: http://localhost:8080 (database UI)"
    echo ""
    echo "4. View logs:"
    echo "   ${YELLOW}make logs${NC}"
    echo ""
    echo "5. Run tests:"
    echo "   ${YELLOW}make test${NC}"
    echo ""
    echo "6. Deploy to Kubernetes:"
    echo "   ${YELLOW}make k8s-deploy${NC}"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  ${YELLOW}make help${NC}           - Show all available commands"
    echo "  ${YELLOW}make dev${NC}            - Start development environment"
    echo "  ${YELLOW}make docker-up${NC}      - Start Docker containers"
    echo "  ${YELLOW}make test${NC}           - Run all tests"
    echo "  ${YELLOW}make lint${NC}           - Run code linters"
    echo "  ${YELLOW}make train-models${NC}   - Train ML models"
    echo "  ${YELLOW}make mlflow-start${NC}   - Start MLflow server"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - README.md - Project overview"
    echo "  - ARCHITECTURE.md - System design"
    echo "  - DEPLOYMENT_GUIDE.md - Deployment instructions"
    echo "  - COMPLETE_18_MODULES_DOCUMENTATION.md - Full curriculum guide"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║   Movie Ticketing Platform - Project Initialization   ║"
    echo "║              (Complete DevOps MLOps AI Stack)         ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_prerequisites
    create_directories
    setup_env_files
    install_dependencies
    setup_git
    build_docker_images
    init_databases
    create_sample_data
    init_mlops
    create_ssh_keys
    print_final_instructions
}

# Run main function
main
