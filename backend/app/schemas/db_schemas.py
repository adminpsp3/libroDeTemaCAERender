from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- Docente Schemas ---
class DocenteBase(BaseModel):
    nombre: str
    apellido: str
    email: str
    dni: str
    rol: str = "docente"

class DocenteCreate(DocenteBase):
    pass

class DocenteResponse(DocenteBase):
    id: int
    class Config:
        from_attributes = True

# --- Curso Schemas ---
class CursoBase(BaseModel):
    anio: int
    division: str

class CursoCreate(CursoBase):
    pass

class CursoResponse(CursoBase):
    id: int
    class Config:
        from_attributes = True

# --- Materia Schemas ---
class MateriaBase(BaseModel):
    nombre: str
    curso_id: int

class MateriaCreate(MateriaBase):
    pass

class MateriaResponse(MateriaBase):
    id: int
    class Config:
        from_attributes = True

# --- LibroTema Schemas ---
class LibroTemaBase(BaseModel):
    docente_id: int
    materia_id: int

class LibroTemaCreate(LibroTemaBase):
    pass

class LibroTemaResponse(LibroTemaBase):
    id: int
    class Config:
        from_attributes = True

# --- RegistroClase Schemas ---
class RegistroClaseBase(BaseModel):
    libro_id: int
    fecha_clase: date
    fecha_carga: Optional[date] = None
    contenidos: str
    actividades: Optional[str] = None
    observaciones: Optional[str] = None

class RegistroClaseCreate(RegistroClaseBase):
    pass

class RegistroClaseResponse(RegistroClaseBase):
    id: int
    class Config:
        from_attributes = True

# --- Nested Schemas for deeper responses ---
class MateriaWithCurso(MateriaResponse):
    curso: CursoResponse

class LibroTemaFull(LibroTemaResponse):
    docente: DocenteResponse
    materia: MateriaWithCurso
    registros: List[RegistroClaseResponse] = []
