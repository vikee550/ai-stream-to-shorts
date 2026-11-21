from fastapi import FastAPI

app = FastAPI(
    title="AI Stream to Shorts",
    description="AI-powered YouTube stream clipping application",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "AI Stream to Shorts is running!",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
