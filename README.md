Financial Analysis Agent API
A robust, scalable API for fetching, storing, and analyzing financial data. This project serves as the foundational data layer for a multi-agent system designed for automated stock analysis and insights.

🚀 Features
Automated Data Pipeline: Fetch historical and fundamental financial data from public sources.

Persistent Caching: Stores financial statements in a PostgreSQL database to minimize redundant API calls and improve performance.

Scalable Architecture: Built with FastAPI and a modular, service-oriented structure for easy expansion.

Vector Database Ready: Integrated with PGVector for future NLP and semantic search capabilities.

Containerized: Fully containerized with Docker for consistent development and deployment environments.

🛠️ Tech Stack
Backend: Python, FastAPI

Database: PostgreSQL, PGVector

Data Libraries: yfinance, pandas

ORM: SQLAlchemy

Validation: Pydantic

Containerization: Docker, Docker Compose

🏗️ Project Architecture
The project follows a clean, scalable structure that separates concerns into distinct layers:

src/api/: Defines the API routers and endpoints.

src/services/: Contains the core business logic (e.g., fetching data from yfinance).

src/db/: Manages database sessions, connections, and ORM models (SQLAlchemy).

src/core/: Handles application-level configuration and settings.

This modular design ensures that the application is maintainable and easy to extend with new features or data sources.

🏁 Getting Started
Follow these instructions to set up the development environment on your local machine.

Prerequisites
Python 3.9+

Docker & Docker Compose

Installation & Setup
Clone the Repository

git clone <your-repository-url>
cd financial-agent

Configure Environment Variables
Create a .env file in the project root by copying the example.

cp .env.example .env

Update the .env file with your database credentials and any necessary API keys. For local development, ensure POSTGRES_HOST is set to localhost.

Launch the Database
This command starts the PostgreSQL database container in the background.

docker-compose up -d

Set Up Python Environment
Create and activate a virtual environment, then install the required packages.

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Run the Application
Start the FastAPI development server.

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

The API is now accessible at http://localhost:8000/docs.

⚙️ API Usage
Interact with the API using any HTTP client or the auto-generated Swagger documentation.

Endpoints
Health Check

GET /health

Verifies that the API is running.

Fetch & Store Financial Statements

POST /api/v1/data/fetch/{ticker}

Triggers the data pipeline to fetch and store the income statement, balance sheet, and cash flow for the specified stock ticker.

Example:

curl -X POST http://localhost:8000/api/v1/data/fetch/MSFT

Get Historical OHLCV Data

GET /api/v1/data/ohlcv/{ticker}

Retrieves historical Open-High-Low-Close-Volume data for the specified ticker.

Example:

curl http://localhost:8000/api/v1/data/ohlcv/MSFT

🚢 Deployment
This application is designed for containerized deployment. The included Dockerfile builds a production-ready image using gunicorn as the web server. To build and run the application container, you would typically use a CI/CD pipeline or run the following commands:

# Build the Docker image
docker build -t financial-agent-api .

# Run the container (example)
docker run -d -p 8000:8000 --env-file .env --name api financial-agent-api

Note: In a real production environment, the database would be a managed service, and environment variables would be injected securely.

🗺️ Roadmap
[ ] Phase 1.2: Implement embedding and storage of financial news articles.

[ ] Phase 2: Develop the first analysis agent to perform sentiment analysis on news.

[ ] Phase 3: Introduce a second agent for quantitative analysis based on stored financial statements.

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.