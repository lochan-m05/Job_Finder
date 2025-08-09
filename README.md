# Job Discovery Platform

A comprehensive AI-powered job discovery platform that uses web scraping, NLP, and machine learning to find and analyze job opportunities based on hashtag searches.

## 🚀 Features

### Core Functionality
- **Hashtag-based Job Search**: Search using hashtags like `#bca #fresher #javascript`
- **Multi-source Scraping**: LinkedIn, Naukri, Indeed, Twitter, and other job boards
- **Real-time Data**: Live scraping with time filters (1h, 24h, 7d, 30d)
- **Contact Extraction**: Automated extraction of recruiter emails, phones, and LinkedIn profiles
- **NLP Analysis**: Job description analysis, skill extraction, and sentiment scoring

### AI & Machine Learning
- **Job Matching**: AI-powered job-profile matching with relevance scores
- **Skill Detection**: Automatic extraction of technical and soft skills
- **Salary Prediction**: ML-based salary estimation
- **Quality Scoring**: Job posting quality assessment
- **Resume Analysis**: Resume-job compatibility scoring

### Advanced Features
- **Anti-bot Protection**: Proxy rotation, CAPTCHA solving, headless browsing
- **Asynchronous Processing**: Celery-based background job processing
- **Real-time Dashboard**: Live analytics and job discovery trends
- **Export Capabilities**: CSV, Excel, PDF export functionality
- **Contact Verification**: Email and phone number validation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   MongoDB       │
│                 │◄──►│                 │◄──►│   Database      │
│ • Dashboard     │    │ • REST API      │    │                 │
│ • Job Search    │    │ • Authentication│    │ • Jobs          │
│ • Analytics     │    │ • Job Processing│    │ • Contacts      │
└─────────────────┘    └─────────────────┘    │ • Users         │
                                              └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         │              │   Celery        │
         │              │   Workers       │
         │              │                 │
         │              │ • Web Scraping  │
         │              │ • NLP Analysis  │
         │              │ • Contact Ext.  │
         │              └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────►│   Redis         │
                        │   Message Broker│
                        └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database with Beanie ODM
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **Selenium**: Web scraping automation
- **spaCy**: Natural language processing
- **Transformers**: AI/ML models for text analysis

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Recharts**: Data visualization
- **Framer Motion**: Animations

### Infrastructure
- **Docker**: Containerization
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Monitoring and metrics
- **Grafana**: Visualization and dashboards

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Make (optional, for convenience commands)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/job-discovery-platform.git
   cd job-discovery-platform
   ```

2. **Set up environment variables**
   ```bash
   cp config.env.example .env
   # Edit .env with your configuration
   ```

3. **Start the platform**
   ```bash
   # Using Make (recommended)
   make setup
   
   # Or using Docker Compose directly
   docker-compose build
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Celery Flower: http://localhost:5555
   - Grafana: http://localhost:3001

### Development Setup

For development with hot reloading:

```bash
# Start development environment
make setup-dev

# Or manually
docker-compose -f docker-compose.dev.yml up -d
```

## 📖 Usage

### Basic Job Search

1. **Navigate to Job Search** (http://localhost:3000/search)
2. **Enter hashtags** like `#python #developer #remote`
3. **Configure filters** (location, experience, salary, etc.)
4. **Start scraping** to discover new opportunities
5. **View results** with contact information and analysis

### Dashboard Analytics

- **Job Trends**: Visualize job discovery patterns
- **Skill Analysis**: Top skills in demand
- **Location Insights**: Geographic job distribution
- **Saved Jobs**: Bookmark interesting opportunities

### Contact Management

- **Automated Extraction**: Emails, phones, LinkedIn profiles
- **Verification**: Email deliverability and phone validation
- **Enrichment**: Additional profile information
- **Export**: Contact lists in various formats

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
MONGODB_URL=mongodb://admin:password123@mongodb:27017/job_discovery?authSource=admin
REDIS_URL=redis://redis:6379/0

# API Keys
OPENAI_API_KEY=your_openai_key
TWOCAPTCHA_API_KEY=your_2captcha_key

# Scraping
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
PROXY_LIST=proxy1:port:user:pass,proxy2:port:user:pass

# Security
SECRET_KEY=your-secret-key-here
```

### Scaling Configuration

```bash
# Scale Celery workers
make scale-workers WORKERS=8

# Scale Chrome nodes for scraping
docker-compose up -d --scale chrome_node=4
```

## 📊 Monitoring

### Available Dashboards

- **Grafana**: http://localhost:3001 (admin/admin123)
  - System metrics
  - Application performance
  - Scraping statistics

- **Flower**: http://localhost:5555
  - Celery task monitoring
  - Worker status
  - Task history

- **Prometheus**: http://localhost:9090
  - Raw metrics data
  - Custom queries

### Logs

```bash
# View all logs
make logs

# Specific service logs
make logs-backend
make logs-celery
make logs-frontend
```

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# With coverage
docker-compose exec backend pytest --cov=app
```

## 🔒 Security

### Anti-bot Measures
- **Proxy Rotation**: Automatic IP switching
- **User Agent Randomization**: Mimic real browsers
- **Request Delays**: Human-like browsing patterns
- **CAPTCHA Solving**: Automated challenge resolution

### Data Protection
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Prevent injection attacks
- **Secure Headers**: OWASP security headers
- **Authentication**: JWT-based user sessions

## 📈 Performance

### Optimization Features
- **Async Processing**: Non-blocking operations
- **Caching**: Redis-based response caching
- **Database Indexing**: Optimized MongoDB queries
- **CDN Ready**: Static asset optimization

### Scaling Guidelines
- **Horizontal Scaling**: Multiple worker instances
- **Database Sharding**: MongoDB cluster support
- **Load Balancing**: Nginx reverse proxy
- **Resource Monitoring**: Prometheus metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation as needed

## 📝 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
POST /api/scraping/jobs        # Start job scraping
GET  /api/jobs                 # Search jobs
GET  /api/jobs/{id}           # Get job details
POST /api/contacts/extract     # Extract contacts
GET  /api/analytics/dashboard  # Dashboard data
```

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Shell access
docker-compose exec backend bash
docker-compose exec frontend sh

# Database shell
docker-compose exec mongodb mongosh

# Stop services
docker-compose down

# Clean up
docker-compose down -v --remove-orphans
```

## 🔧 Troubleshooting

### Common Issues

**Chrome/Selenium Issues**
```bash
# Restart selenium services
docker-compose restart selenium_hub chrome_node

# Check Chrome installation
docker-compose exec backend google-chrome --version
```

**Database Connection**
```bash
# Check MongoDB status
docker-compose exec mongodb mongosh --eval "db.stats()"

# Reset database
docker-compose down -v
docker-compose up -d mongodb
```

**Celery Workers Not Processing**
```bash
# Restart workers
docker-compose restart celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [React](https://reactjs.org/) for the frontend library
- [spaCy](https://spacy.io/) for NLP capabilities
- [Selenium](https://selenium.dev/) for web automation
- [MongoDB](https://www.mongodb.com/) for the database

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review existing issues and discussions

---

**Happy Job Hunting! 🎯**
