import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.database.connection import SessionLocal
from app.database import models
from sqlalchemy.orm import joinedload

def test_query():
    db = SessionLocal()
    try:
        libro_id = 1
        print(f"Testing query for libro_id: {libro_id}")
        
        # This is the same logic as in routers/libros.py
        libro = db.query(models.LibroTema)\
            .options(
                joinedload(models.LibroTema.materia).joinedload(models.Materia.curso)
            )\
            .filter(models.LibroTema.id == libro_id).first()
        
        if not libro:
            print("Libro not found in DB")
            return

        print(f"Libro found: {libro.materia.nombre}")

        registros = db.query(models.RegistroClase)\
            .filter(models.RegistroClase.libro_id == libro_id)\
            .all()
        
        print(f"Found {len(registros)} records")
        for r in registros:
            print(f"Record ID: {r.id}, Fecha: {r.fecha_clase}, Contenidos: {r.contenidos[:20]}...")

    except Exception as e:
        print("\n--- ERROR DETECTED ---")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
