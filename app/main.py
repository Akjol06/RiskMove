from fastapi import FastAPI
from app.interfaces.api import router
import uvicorn

app = FastAPI(
    title="Credit Scoring API",
    description="Intelligent system for credit risk assessment following DDD principles.",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
