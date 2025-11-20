from fastapi import FastAPI
from app.routers import individual_router


app = FastAPI(
    title="Family Tree API",
    version="1.0.0"
)

app.include_router(individual_router.router)

@app.get("/")
def root():
    return {"message":"Family Tree API is running 🚀"}