from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, DB_PATH
from routers import auth, products, researcher, warehouses, iot, messaging, chat

app = FastAPI(
    title="OptiStock Solutions API",
    description="API REST pour le système d'aide à la décision logistique OptiStock",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(researcher.router)
app.include_router(warehouses.router)
app.include_router(iot.router)
app.include_router(messaging.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    db_exists = os.path.exists(DB_PATH)
    return {
        "status": "ok",
        "database": "connected" if db_exists else "missing",
        "version": "2.0.0",
    }
