from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base

app = FastAPI(title="ApplyPilot AI")

Base.metadata.create_all(bind=engine)

app.include_router(router)


@app.get("/test")
def test():
    return {"message": "Backend working 🚀"}