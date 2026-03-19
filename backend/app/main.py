from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import auth, libros
import os

app = FastAPI(title="Libro de Temas Digital")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(libros.router)

from fastapi.responses import RedirectResponse

@app.get("/")
async def read_root():
    return RedirectResponse(url="/login")
