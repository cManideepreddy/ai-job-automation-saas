from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base

# ✅ Create app FIRST
app = FastAPI(title="ApplyPilot AI")

# ✅ Then create DB
Base.metadata.create_all(bind=engine)

# ✅ THEN define routes
@app.get("/test")
def test():
    return {"message": "working"}

# ✅ Include router
app.include_router(router)