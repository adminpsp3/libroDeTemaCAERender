from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from ..core import security
from ..database.connection import get_db
from sqlalchemy.orm import Session
from ..database import models

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    payload = security.decode_access_token(token)
    if not payload:
        return None
    
    email = payload.get("email")
    dni_raw = payload.get("dni")
    user = db.query(models.Docente).filter(models.Docente.email == email).first()
    if user:
        # Set transient attribute for raw DNI
        user.dni_raw = dni_raw if dni_raw else ""
    return user

async def login_required(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=302, detail="Not authenticated", headers={"Location": "/login"})
    return user

async def admin_required(user = Depends(get_current_user)):
    if not user or user.rol != "admin":
        raise HTTPException(status_code=302, detail="Admin required", headers={"Location": "/login"})
    return user

async def any_role_required(user = Depends(get_current_user)):
    # Any authenticated user with a valid role can access the dashboard/libros
    if not user or user.rol not in ["docente", "autoridad", "admin"]:
        raise HTTPException(status_code=302, detail="Not authorized", headers={"Location": "/login"})
    return user

async def docente_required(user = Depends(get_current_user)):
    # Allows Docente, Autoridad and Admin for teacher-facing routes (with role-based logic inside)
    if not user or user.rol not in ["docente", "autoridad", "admin"]:
        raise HTTPException(status_code=302, detail="Docente required", headers={"Location": "/login"})
    return user
