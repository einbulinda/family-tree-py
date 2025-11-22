from fastapi import FastAPI
from app.api.individuals import router as individuals_router
from app.api.auth import router as auth_router
from app.api.relationship import router as relation_router


app = FastAPI(
    title="Family Tree API",
    version="1.0.0"
)

app.include_router(individuals_router)
app.include_router(auth_router)
app.include_router(relation_router)

@app.get("/")
def root():
    return {"message":"Family Tree API is running 🚀"}