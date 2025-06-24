# Farmily TRACE API

The official API for the TRACE Digital Commodities Exchange - a platform for agricultural commodity trading and traceability.

## Overview

TRACE is a digital platform that enables farmers, traders, and businesses to list, trade, and trace agricultural commodities. The API provides user authentication, business verification, and marketplace functionality for agricultural products.

## Features

- **User Management**: Registration and authentication with phone numbers and PINs
- **Business Verification**: KYB (Know Your Business) document management
- **Commodity Listings**: Create and manage agricultural product listings
- **JWT Authentication**: Secure API access with Bearer tokens
- **Multi-tier User System**: Different user tiers with varying capabilities

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with python-jose
- **Migration**: Alembic
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd farmily
```

2. Create virtual environment:
```bash
python -m venv farmilyenv
source farmilyenv/bin/activate  # On Windows: farmilyenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export DATABASE_URL=postgresql://user:password@localhost/mydatabase
export SECRET_KEY=your-secret-key
export ALGORITHM=HS256
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn traceapi.main:app --reload
```

### Docker Setup

1. Start with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login/token` - Login and get access token
- `GET /api/v1/users/profile` - Get current user profile

### Listings
- `POST /api/v1/listings` - Create commodity listing
- `GET /api/v1/listings` - Get all listings
- `GET /api/v1/listings/{id}` - Get specific listing
- `PUT /api/v1/listings/{id}` - Update listing
- `DELETE /api/v1/listings/{id}` - Delete listing

## Database Models

### User
- Phone number-based authentication
- PIN-based security
- User tiers (TIER_0, TIER_1, etc.)
- Business association

### Business
- CAC number verification
- Admin designation
- KYB document management
- Member management

### Listing
- Commodity details (name, quantity, price)
- Location information (LGA, State)
- Incoterms support
- Seller association

## Authentication

The API uses JWT Bearer tokens for authentication:

1. Register or login to get an access token
2. Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Development

### Project Structure
```
traceapi/
├── api/v1/endpoints/    # API route handlers
├── core/               # Configuration and security
├── crud/               # Database operations
├── db/                 # Database models and session
├── schemas/            # Pydantic models
├── utils/              # Utility functions
└── main.py            # FastAPI application
```

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary software developed for the TRACE Digital Commodities Exchange.

## Contact

For questions or support, contact: akeem.a@hexcore.ng