

# Multi-Agent Fundamental Stock Analysis Engine

A scalable and automated financial data analysis engine designed to serve as the foundational data layer for a multi-agent system for automated stock analysis. This project provides a robust backend service for fetching, storing, and analyzing financial data from public sources.

[](https://opensource.org/licenses/MIT)
[](https://www.google.com/search?q=https.shields.io/badge/python-3.9-blue.svg)
[](https://www.docker.com/)

-----

## 🌟 Key Features

  * **🤖 Automated Data Pipeline:** Automatically fetches historical and fundamental financial data from public sources using `yfinance`.
  * **⚡ Persistent Caching:** Stores financial statements and historical data in a PostgreSQL database to improve performance and reduce redundant API calls.
  * **🚀 Scalable Architecture:** Built with FastAPI in a modular, service-oriented architecture, ensuring high performance and scalability.
  * **🧠 Vector Database Ready:** Integrated with PGVector for future NLP and AI-powered capabilities, such as sentiment analysis and financial news embeddings.
  * **🐳 Fully Containerized:** Comes with a complete Docker and Docker Compose setup for easy and consistent deployment.

-----

## 🛠️ Tech Stack

  * **Backend:** Python, FastAPI
  * **Database:** PostgreSQL, PGVector
  * **Data Libraries:** yfinance, pandas
  * **ORM:** SQLAlchemy
  * **Validation:** Pydantic
  * **Containerization:** Docker, Docker Compose

-----

## 🏗️ Project Architecture

The project follows a clean, service-oriented architecture to separate concerns and improve maintainability.

```
src/
├── api/          # API routers and endpoints
├── services/     # Core business logic and services
├── db/           # Database sessions, connections, and ORM models
└── core/         # Application-level configuration
```

-----

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

  * Docker and Docker Compose
  * Python 3.9+
  * Poetry (for managing Python dependencies)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/rahulbastia00/Multi-Agent-Fundamental-Stock-Analysis-Engine.git
    cd Multi-Agent-Fundamental-Stock-Analysis-Engine
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root of the project and add the necessary database configuration. You can copy the example file:

    ```bash
    cp .env.example .env
    ```

    Then, update the `.env` file with your database credentials.

3.  **Launch the Database:**
    Start the PostgreSQL database using Docker Compose:

    ```bash
    docker-compose up -d db
    ```

4.  **Set up the Python Environment and Install Dependencies:**

    ```bash
    poetry install
    ```

5.  **Run the Application:**

    ```bash
    poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ```

    The API will be available at `http://localhost:8000`.

-----

## 📈 API Usage

The application provides the following API endpoints:

  * **Health Check:**
    `GET /health` - Checks the health of the application.

  * **Fetch and Store Financial Data:**
    `POST /api/v1/data/fetch/{ticker}` - Fetches and stores financial statements for a given stock ticker.

  * **Get Historical Stock Data:**
    `GET /api/v1/data/ohlcv/{ticker}` - Retrieves historical Open-High-Low-Close-Volume (OHLCV) data for a given ticker.

You can access the interactive API documentation at `http://localhost:8000/docs`.

-----

## 🚢 Deployment

This application is designed to be deployed as a containerized service. You can build and run the Docker image using the following commands:

1.  **Build the Docker Image:**

    ```bash
    docker-compose build app
    ```

2.  **Run the Application:**

    ```bash
    docker-compose up -d app
    ```

-----

## 🗺️ Roadmap

This project is the first phase of a larger multi-agent system for stock analysis. Here is the planned roadmap:

  * **Phase 1.2:** Implement embedding and storage of financial news articles.
  * **Phase 2:** Develop a sentiment analysis agent to analyze financial news.
  * **Phase 3:** Introduce a quantitative analysis agent to perform calculations on the stored financial data.
  * **Phase 4:** Create a master agent that orchestrates the other agents to provide a holistic stock analysis.

-----

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for more details.
