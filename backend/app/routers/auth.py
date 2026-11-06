
from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..services.auth_service import AuthService
from ..core.security import create_access_token
from ..dependencies.auth_dependency import get_current_user
import os

router = APIRouter()

# Configuración de la ruta de las plantillas
templates_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates"
)

templates = Jinja2Templates(directory=templates_path)


# ==========================================
# PÁGINA DE INICIO DE SESIÓN
# ==========================================

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


# ==========================================
# PROCESO DE AUTENTICACIÓN
# ==========================================

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    dni: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.authenticate_user(db, email, dni)

        # Validar usuario
        if not user:
            return templates.TemplateResponse(
                request=request,
                name="components/login_error.html",
                context={
                    "request": request,
                    "error": "Usuario no válido"
                }
            )

        # Crear token de acceso
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "email": user.email,
                "rol": user.rol,
                "dni": dni
            }
        )

        # Redireccionar según el rol del usuario
        redirect_url = (
            "/admin"
            if user.rol == "admin"
            else "/dashboard"
        )

        response = Response(
            status_code=200,
            headers={"HX-Redirect": redirect_url}
        )

        # Configurar cookie de autenticación
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=3600 * 8
        )

        return response

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="components/login_error.html",
            context={
                "request": request,
                "error": f"Error del sistema: {str(e)}"
            }
        )


# ==========================================
# CERRAR SESIÓN
# ==========================================

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


# ==========================================
# PANEL DEL DOCENTE
# ==========================================

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user=Depends(get_current_user)
):
    if not user or user.rol not in ["docente", "autoridad", "admin"]:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user
        }
    )


# ==========================================
# PANEL DE ADMINISTRACIÓN
# ==========================================

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    user=Depends(get_current_user)
):
    if not user or user.rol != "admin":
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "request": request,
            "user": user
        }
    )
