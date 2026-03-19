from fastapi import APIRouter, Depends, Request, HTTPException, Response, Form
from datetime import date
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from ..database.connection import get_db
from ..database import models
from ..dependencies.auth_dependency import get_current_user, docente_required
import os

router = APIRouter(prefix="/libros", tags=["Libros"])

# Setup templates path
templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)

@router.get("/docente", response_class=HTMLResponse)
async def get_libros_docente(
    request: Request, 
    db: Session = Depends(get_db), 
    user: models.Docente = Depends(docente_required)
):
    # Authority roles see everything, teachers only see their own
    query = db.query(models.LibroTema)\
        .options(
            joinedload(models.LibroTema.materia).joinedload(models.Materia.curso),
            joinedload(models.LibroTema.docente)
        )
    
    if user.rol not in ["admin", "autoridad"]:
        query = query.filter(models.LibroTema.docente_id == user.id)
    
    libros = query.all()
    
    return templates.TemplateResponse("libros_docente.html", {
        "request": request, 
        "user": user,
        "libros": libros
    })

@router.get("/{libro_id}", response_class=HTMLResponse)
async def get_libro_detail(
    libro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    # Fetch the book with its relations
    libro = db.query(models.LibroTema)\
        .options(
            joinedload(models.LibroTema.materia).joinedload(models.Materia.curso)
        )\
        .filter(models.LibroTema.id == libro_id).first()
    
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    # Check ownership unless it's an authority role
    if user.rol not in ["admin", "autoridad"] and libro.docente_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para ver este libro")

    # Fetch records for this book, newest first
    registros = db.query(models.RegistroClase)\
        .filter(models.RegistroClase.libro_id == libro_id)\
        .order_by(models.RegistroClase.fecha_clase.desc())\
        .all()

    # Dictionary for Spanish day names
    dias_semana = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    # Add day name to each record object dynamically for the template
    for r in registros:
        if r.fecha_clase:
            r.dia_semana = dias_semana.get(r.fecha_clase.weekday(), "Desconocido")
        else:
            r.dia_semana = "Sin fecha"

    return templates.TemplateResponse("registro_clases.html", {
        "request": request,
        "user": user,
        "libro": libro,
        "registros": registros,
        "today": date.today()
    })

@router.delete("/registro/{registro_id}")
async def delete_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    if user.rol != "docente":
        raise HTTPException(status_code=403, detail="Las autoridades solo tienen permiso de lectura")
        
    # Security check: ensure the record belongs to a book owned by the teacher
    registro = db.query(models.RegistroClase).join(models.LibroTema).filter(
        models.RegistroClase.id == registro_id,
        models.LibroTema.docente_id == user.id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    db.delete(registro)
    db.commit()
    return Response(status_code=200)

@router.get("/registro/{registro_id}/edit", response_class=HTMLResponse)
async def get_edit_modal(
    registro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    registro = db.query(models.RegistroClase).join(models.LibroTema).filter(
        models.RegistroClase.id == registro_id,
        models.LibroTema.docente_id == user.id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    dias_semana = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}
    registro.dia_semana = dias_semana.get(registro.fecha_clase.weekday(), "Desconocido") if registro.fecha_clase else "Sin fecha"

    return templates.TemplateResponse("components/modal_edit_registro.html", {
        "request": request,
        "registro": registro
    })

@router.post("/registro/{registro_id}/edit", response_class=HTMLResponse)
async def update_registro(
    registro_id: int,
    request: Request,
    fecha_clase: date = Form(...),
    contenidos: str = Form(...),
    actividades: str = Form(None),
    observaciones: str = Form(None),
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    if user.rol != "docente":
        raise HTTPException(status_code=403, detail="Las autoridades solo tienen permiso de lectura")
        
    registro = db.query(models.RegistroClase).join(models.LibroTema).filter(
        models.RegistroClase.id == registro_id,
        models.LibroTema.docente_id == user.id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Update fields
    registro.fecha_clase = fecha_clase
    registro.contenidos = contenidos
    registro.actividades = actividades
    registro.observaciones = observaciones
    registro.fecha_carga = date.today() # Auto update load date

    db.commit()
    db.refresh(registro)

    # Recalculate day for the component
    dias_semana = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}
    dia_semana = dias_semana.get(registro.fecha_clase.weekday(), "Desconocido") if registro.fecha_clase else "Sin fecha"

    # We need to pass the "index" which is class number. 
    # For now we'll just return the item. To keep the class number correct after an edit, 
    # we'd ideally need the original index. But for a quick update, we can just passthru a "Clase" text.
    # A better way is to pass the correct class number by counting.
    count = db.query(models.RegistroClase).filter(
        models.RegistroClase.libro_id == registro.libro_id,
        models.RegistroClase.fecha_clase <= registro.fecha_clase
    ).count()

    return templates.TemplateResponse("components/registro_item.html", {
        "request": request,
        "registro": registro,
        "dia_semana": dia_semana,
        "index": count
    })

@router.get("/{libro_id}/nuevo", response_class=HTMLResponse)
async def get_nuevo_modal(
    libro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    libro = db.query(models.LibroTema)\
        .options(joinedload(models.LibroTema.materia).joinedload(models.Materia.curso))\
        .filter(models.LibroTema.id == libro_id).first()
    
    if not libro or libro.docente_id != user.id:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    return templates.TemplateResponse("components/modal_nuevo_registro.html", {
        "request": request,
        "user": user,
        "libro": libro,
        "today": date.today()
    })

@router.post("/{libro_id}/nuevo")
async def create_registro(
    libro_id: int,
    request: Request,
    fecha_clase: date = Form(...),
    contenidos: str = Form(...),
    actividades: str = Form(None),
    observaciones: str = Form(None),
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    if user.rol != "docente":
        raise HTTPException(status_code=403, detail="Las autoridades solo tienen permiso de lectura")
        
    libro = db.query(models.LibroTema).filter(models.LibroTema.id == libro_id).first()
    if not libro or libro.docente_id != user.id:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    nuevo_registro = models.RegistroClase(
        libro_id=libro_id,
        fecha_clase=fecha_clase,
        fecha_carga=date.today(),
        contenidos=contenidos,
        actividades=actividades,
        observaciones=observaciones
    )

    db.add(nuevo_registro)
    db.commit()

    # After saving, we redirect to refresh the page and show the new record
    # Since it's HTMX, we can do a full redirect or just return the page
    return RedirectResponse(url=f"/libros/{libro_id}", status_code=303)

@router.delete("/{libro_id}/delete_all")
async def delete_all_registros(
    libro_id: int,
    db: Session = Depends(get_db),
    user: models.Docente = Depends(docente_required)
):
    if user.rol != "docente":
        raise HTTPException(status_code=403, detail="Las autoridades solo tienen permiso de lectura")
        
    libro = db.query(models.LibroTema).filter(models.LibroTema.id == libro_id).first()
    if not libro or libro.docente_id != user.id:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Delete all records associated with this book
    db.query(models.RegistroClase).filter(models.RegistroClase.libro_id == libro_id).delete()
    db.commit()
    
    # Return redirect header for HTMX to refresh the whole page
    return Response(headers={"HX-Redirect": f"/libros/{libro_id}"})
