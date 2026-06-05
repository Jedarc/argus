from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Argus", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Routers registered here as they are implemented:
# from api.routers import investigations, modules, ws
# app.include_router(investigations.router, prefix="/investigations")
# app.include_router(modules.router, prefix="/modules")
# app.include_router(ws.router)
