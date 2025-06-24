"""main.py"""

from fastapi import FastAPI
from traceapi.api.api_v1.endpoints import users as user_router
from traceapi.api.api_v1.endpoints import listings as listing_router
from traceapi.db.base_class import Base
from traceapi.db.session import engine

# This command will create the database tables based on our SQLAlchemy models
# It's good for initial setup. For production and updates, we will use Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TRACE Platform API",
    description="The official API for the TRACE Digital Commodities Exchange.",
    version="1.0.0"
)

# All routes in 'users.py' will be prefixed with '/api/v1/users'
app.include_router(user_router.router, prefix="/api/v1/users", tags=["Users"])

# Include the new marketplace listings router
app.include_router(listing_router.router, prefix="/api/v1/listings", tags=["Listings"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Farmily TRACE API"}
