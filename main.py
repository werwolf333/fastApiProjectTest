from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from database import init_db
from chat_module import router as chat_router
from auth_module import router as auth_router

app = FastAPI()
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(chat_router.router)
app.include_router(auth_router.router)
