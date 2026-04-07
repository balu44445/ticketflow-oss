from fastapi import FastAPI

from app.api.routes import router
from app.core.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TicketFlow OSS", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
