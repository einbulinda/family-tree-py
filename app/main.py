from fastapi import FastAPI
from app.api.individuals import router as individuals_router


app = FastAPI(
    title="Family Tree API",
    version="1.0.0"
)

app.include_router(individuals_router)

@app.get("/")
def root():
    return {"message":"Family Tree API is running 🚀"}