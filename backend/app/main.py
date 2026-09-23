from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import tasks, techniques, resources, insights, experiments, digest

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Technique Library API")

# CORS for frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(techniques.router, prefix="/techniques", tags=["techniques"])
app.include_router(resources.router, prefix="/resources", tags=["resources"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
app.include_router(digest.router, prefix="/digest", tags=["digest"])


@app.get("/")
def read_root():
    return {"message": "ML Technique Library API"}
