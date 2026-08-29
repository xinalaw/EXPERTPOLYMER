from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.analysis_routes import router as analysis_router
from app.routes.user_routes import router as user_router
from app.routes.invite_routes import router as invite_router
from app.routes.director_routes import router as director_router
from app.routes.log_routes import router as log_router
from app.routes.websocket_routes import router as websocket_router

app = FastAPI(
    title="Scientific System Backend API",
    description="API для системы анализа изображений полимерных композиционных материалов",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(user_router)
app.include_router(invite_router)
app.include_router(director_router)
app.include_router(log_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "Science Admin Panel API"}
