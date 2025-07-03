"""Lambda handler for FastAPI app"""

from mangum import Mangum
from traceapi.main import app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")