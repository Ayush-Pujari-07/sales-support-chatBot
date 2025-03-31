# Sales Support ChatBot

A sales support chatbot built with FastAPI and Streamlit that leverages LangChain, OpenAI, and various other technologies to provide intelligent sales assistance.

## Features

- User authentication system
- Real-time chat interface
- Integration with OpenAI GPT models
- Document search capabilities via Exa
- Image generation support via DALL-E
- Redis caching
- PostgreSQL database for data persistence
- Docker containerization

## Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Docker and Docker Compose (optional)

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
pip install -r requirements/requirements_dev.txt
```

4. Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Configure the following environment variables in `.env`:
```env
# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=your_openai_api_key
EXA_API_KEY=your_exa_api_key

# JWT Configuration
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=210000
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

1. Start all services:
```bash
docker-compose up -d
```

### Manual Setup

1. Start the backend server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 9000 --reload
```

2. Start the frontend application:
```bash
streamlit run frontend/main.py
```

The application will be available at:
- Backend API: http://localhost:9000
- Frontend UI: http://localhost:8501
- API Documentation: http://localhost:9000/docs

## Project Structure

```
sales-support-chatBot/
├── src/                    # Backend source code
│   ├── auth/              # Authentication related modules
│   ├── chat/              # Chat functionality
│   └── db/                # Database models and utilities
├── frontend/              # Streamlit frontend application
├── migrations/            # Database migrations
├── requirements/          # Project dependencies
└── docker-compose.yaml    # Docker compose configuration
```

## Features

### Authentication
- User registration
- Login with JWT tokens
- Refresh token mechanism

### Chat Interface
- Real-time chat with AI assistant
- Support for text and image generation
- Context-aware conversations
- Integration with external knowledge sources

### Admin Interface
- Database management via Adminer (localhost:8080)
- Redis insights (localhost:8001)

## Development

### Running Tests
```bash
pytest tests/
```

### Creating New Migrations
```bash
alembic revision --autogenerate -m "description"
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.