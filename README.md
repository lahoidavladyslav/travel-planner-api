# Travel Planner API

A RESTful API built for managing travel projects and planning trips. This application allows users to create projects, add places of interest (validated via the Art Institute of Chicago API), and track their visiting progress.

## Tech Stack
- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy + SQLite**: Database and ORM for data persistence.
- **Httpx**: Asynchronous HTTP client for third-party API integration.
- **Pydantic**: Data validation and settings management.
- **Docker**: Containerization for easy deployment.

## Key Features
- **Project Management**: Create, update, list, and delete travel projects.
- **Third-party Validation**: All places are validated against the [Art Institute of Chicago API](https://api.artic.edu/docs/) before being added.
- **Business Logic Constraints**:
  - Maximum of 10 places per project.
  - Projects cannot be deleted if any place is already marked as "visited".
  - Automatic project completion once all included places are marked as visited.
- **Caching**: Implemented basic in-memory caching for external API responses to improve performance.

## Getting Started

### Prerequisites
- Docker and Docker Compose (Recommended)
- OR Python 3.10+

### Installation & Running (Docker)
1. Clone the repository.
2. Run the following command in the root directory:
   ```bash
   docker-compose up --build

### Local setup
1. Install dependencies: pip install -r requirements.txt
2. Run server: uvicorn main:app --reload

### API Documentation
1. Swagger UI: http://localhost:8000/docs
2. ReDoc: http://localhost:8000/redoc

### Decisions & Assumptions
- Framework: FastAPI for high performance and auto-documentation.
- Database: SQLite for simplicity and meeting the 2-hour timeframe.
- Validation: Place IDs are verified against the Art Institute of Chicago API before being saved to the database.