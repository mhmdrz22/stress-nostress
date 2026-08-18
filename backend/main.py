from fastapi import FastAPI
from backend.routers import stress, sync
from backend.database import engine, Base

app = FastAPI(
    title="ArameshYar Cloud API",
    description="Backend API for Neuro-Symbolic Stress Detection App",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(stress.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ArameshYar API is running"}
