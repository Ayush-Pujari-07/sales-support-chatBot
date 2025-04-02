# Sales Support ChatBot

A sales support chatbot built with FastAPI and Streamlit that leverages LangChain, OpenAI, and various other technologies to provide intelligent sales assistance.

## Features

### Authentication
- User registration and login system
- JWT-based authentication with access and refresh tokens
- Secure password hashing with bcrypt

### Chat Interface 
- Real-time chat with AI assistant
- Context-aware conversations powered by GPT-4/GPT-3.5
- Document search capabilities via Exa API integration
- Image generation using DALL-E 2/3 models
- Support for streaming responses

### Technical Features
- FastAPI backend with async support 
- Streamlit frontend for user interface
- PostgreSQL database with SQLAlchemy ORM
- Redis for session management and caching
- Docker containerization with docker-compose
- Alembic migrations for database versioning

## Prerequisites

- Python 3.11+
- PostgreSQL 
- Redis
- Docker and Docker Compose (optional)
- OpenAI API key
- Exa API key

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd sales-support-chatBot
```

2. Create and activate a virtual environment:
```bash 
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash 
pip install -r requirements.txt
```

4. Copy the example environment file:
```bash
cp .env.example .env
```

Configure the following environment variables in `.env`:
```env
# Database 
DB_USER=your_db_user
DB_PASSWORD=your_db_password 
DB_NAME=your_db_name
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost 
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=your_openai_api_key
EXA_API_KEY=your_exa_api_key

# JWT
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=210000

# App Settings
SITE_DOMAIN=127.0.0.1
ENVIRONMENT=DEVELOPMENT
SECURE_COOKIES=false

# CORS
CORS_ORIGINS=["http://localhost:3000"]
CORS_HEADERS=["*"]
```

## Database Setup

1. Initialize the database:
```bash
python -m src.db.manage
```

2. Run migrations:
```bash
alembic upgrade head
```

## Running the Application

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Setup

1. Start backend server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 9000 --reload
```

2. Start frontend:
```bash
streamlit run frontend/main.py
```

Access points:
- Backend API: http://localhost:9000
- Frontend UI: http://localhost:8501 
- API Documentation: http://localhost:9000/docs
- Database Admin (Adminer): http://localhost:8080

## Project Structure

```
sales-support-chatBot/
├── src/                    # Backend source code
│   ├── auth/              # Authentication modules
│   ├── chat/              # Chat functionality 
│   └── db/                # Database models and utilities
├── frontend/              # Streamlit frontend
│   ├── pages/            # Frontend page components
│   └── streamlit_navigation.py
├── migrations/            # Database migrations
├── requirements/          # Project dependencies
├── tests/                # Test files
└── docker-compose.yaml    # Docker compose config
```

## Development

### Running Tests
```bash
pytest tests/
```

### Creating Migrations
```bash
alembic revision --autogenerate -m "description"
```

### Pre-commit Hooks
The project uses pre-commit hooks for:
- YAML validation
- End of file fixing
- Line ending normalization
- Trailing whitespace removal
- Debug statement checks
- Black code formatting

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.