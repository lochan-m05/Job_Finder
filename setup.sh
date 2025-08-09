#!/bin/bash

# Job Discovery Platform Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if ports are available
check_ports() {
    local ports=(3000 8000 27017 6379 5555 3001 9090)
    for port in "${ports[@]}"; do
        if lsof -i :$port &> /dev/null; then
            print_warning "Port $port is already in use. Please stop the service using this port or modify docker-compose.yml"
        fi
    done
}

# Create environment file
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        if [ -f config.env.example ]; then
            cp config.env.example .env
            print_success "Created .env file. Please edit it with your configuration."
        else
            print_error "config.env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p data
    mkdir -p backups
    mkdir -p notebooks
    mkdir -p monitoring
    mkdir -p nginx/ssl
    print_success "Directories created"
}

# Download required models and dependencies
download_dependencies() {
    print_status "Checking for required dependencies..."
    
    # Create a simple script to download spaCy model
    cat > download_models.py << 'EOF'
import subprocess
import sys

def download_spacy_model():
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("spaCy model already installed")
        except OSError:
            print("Downloading spaCy model...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            print("spaCy model downloaded successfully")
    except ImportError:
        print("spaCy not installed yet, will be installed with Docker build")

if __name__ == "__main__":
    download_spacy_model()
EOF
    
    if command -v python3 &> /dev/null; then
        python3 download_models.py
    fi
    
    rm -f download_models.py
}

# Build and start services
start_services() {
    print_status "Building Docker images..."
    docker-compose build
    
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Services started successfully"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Show service URLs
show_urls() {
    echo ""
    print_success "Job Discovery Platform is ready! 🚀"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo "  📱 Frontend:          http://localhost:3000"
    echo "  🔧 Backend API:       http://localhost:8000"
    echo "  📚 API Docs:          http://localhost:8000/docs"
    echo "  🌸 Celery Flower:     http://localhost:5555"
    echo "  📊 Grafana:           http://localhost:3001 (admin/admin123)"
    echo "  📈 Prometheus:        http://localhost:9090"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo "  make logs              # View all logs"
    echo "  make shell-backend     # Access backend shell"
    echo "  make shell-db          # Access MongoDB shell"
    echo "  make status            # Check service status"
    echo "  make down              # Stop all services"
    echo ""
    echo -e "${GREEN}Happy job hunting! 🎯${NC}"
}

# Main setup function
main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              Job Discovery Platform Setup                     ║"
    echo "║                                                               ║"
    echo "║  AI-powered job discovery with real-time scraping & NLP      ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_docker
    check_ports
    
    # Setup environment
    setup_env
    create_directories
    download_dependencies
    
    # Start services
    start_services
    
    # Show completion message
    show_urls
}

# Handle script interruption
trap 'print_error "Setup interrupted. Run docker-compose down to clean up."; exit 1' INT

# Run main function
main "$@"
