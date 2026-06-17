from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database.repository import Repository
from app.daily_runner import run_daily_pipeline
from datetime import datetime
from pydantic import BaseModel, EmailStr


app = FastAPI(
    title="AI News Aggregator API",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"


# -------------------------------------------------
# Request Models
# -------------------------------------------------

class SubscribeRequest(BaseModel):
    email: EmailStr


# -------------------------------------------------
# CORS
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Static Files
# -------------------------------------------------

if FRONTEND_DIR.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=FRONTEND_DIR),
        name="frontend",
    )


# -------------------------------------------------
# Home Page
# -------------------------------------------------

@app.get("/")
def home():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "AI News Aggregator API Running"
    }


# -------------------------------------------------
# Dashboard Stats
# -------------------------------------------------

@app.get("/api/stats")
def get_stats():

    repo = Repository()

    articles = repo.get_recent_digests(hours=10000)
    subscribers = repo.get_subscriber_count()

    return {
        "articles": len(articles),
        "subscribers": subscribers,
        "emails_sent": subscribers,
        "sources": 3
    }


# -------------------------------------------------
# Latest Articles
# -------------------------------------------------

@app.get("/api/articles")
def get_articles():

    repo = Repository()

    articles = repo.get_recent_digests(hours=10000)

    return articles


# -------------------------------------------------
# Today's Digest
# -------------------------------------------------

@app.get("/api/digest")
@app.get("/api/digest/today")
def get_digest():

    repo = Repository()

    return repo.get_recent_digests(hours=24)


# -------------------------------------------------
# Subscribers List
# -------------------------------------------------

@app.get("/api/subscribers")
def subscribers():

    repo = Repository()

    users = repo.get_all_subscribers()

    return [
        {
            "email": user.email,
            "active": user.active,
            "subscribed_at": user.subscribed_at,
        }
        for user in users
    ]


# -------------------------------------------------
# Subscribe
# -------------------------------------------------

@app.post("/api/subscribe")
def subscribe(request: SubscribeRequest):

    repo = Repository()

    if repo.subscriber_exists(request.email):
        raise HTTPException(
            status_code=400,
            detail="Email already subscribed."
        )

    subscriber = repo.create_subscriber(request.email)

    return {
        "success": True,
        "message": "Successfully subscribed!",
        "subscriber": {
            "email": subscriber.email,
            "active": subscriber.active,
            "subscribed_at": subscriber.subscribed_at,
        },
    }


# -------------------------------------------------
# Unsubscribe
# -------------------------------------------------

@app.post("/api/unsubscribe")
def unsubscribe(request: SubscribeRequest):

    repo = Repository()

    success = repo.unsubscribe(request.email)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Subscriber not found."
        )

    return {
        "success": True,
        "message": "Successfully unsubscribed."
    }


# -------------------------------------------------
# Pipeline Logs
# -------------------------------------------------

@app.get("/api/logs")
def get_logs():

    return {
        "logs": [
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "SUCCESS",
                "message": "AI News Aggregator is running successfully."
            }
        ]
    }


# -------------------------------------------------
# Run Daily Pipeline
# -------------------------------------------------

@app.post("/api/run-digest")
def run_digest():

    result = run_daily_pipeline()

    return {
        "success": result.get("success", False),
        "message": result.get(
            "message",
            "Pipeline execution completed."
        ),
        "result": result
    }
