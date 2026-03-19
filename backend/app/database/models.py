from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from .connection import Base

class Docente(Base):
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    dni = Column(String(255))
    rol = Column(String(20), default="docente")

    # Relationships
    libros = relationship("LibroTema", back_populates="docente")


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer)
    division = Column(String(50))

    # Relationships
    materias = relationship("Materia", back_populates="curso")


class Materia(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    curso_id = Column(Integer, ForeignKey("cursos.id"))

    # Relationships
    curso = relationship("Curso", back_populates="materias")
    libros = relationship("LibroTema", back_populates="materia")


class LibroTema(Base):
    __tablename__ = "libros_tema"

    id = Column(Integer, primary_key=True, index=True)
    docente_id = Column(Integer, ForeignKey("docentes.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))

    # Relationships
    docente = relationship("Docente", back_populates="libros")
    materia = relationship("Materia", back_populates="libros")
    registros = relationship("RegistroClase", back_populates="libro")


class RegistroClase(Base):
    __tablename__ = "registros_clase"

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(Integer, ForeignKey("libros_tema.id"))
    fecha_clase = Column(Date)
    fecha_carga = Column(Date)
    contenidos = Column(Text)
    actividades = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    # Relationships
    libro = relationship("LibroTema", back_populates="registros")
