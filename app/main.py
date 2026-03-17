from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Job Automation SaaS")

app.include_router(router)