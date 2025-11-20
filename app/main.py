from fastapi import FastAPI


app = FastAPI(
    title="Family Tree API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message":"Family Tree API is running 🚀"}