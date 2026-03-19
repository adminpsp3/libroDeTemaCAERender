import sys
import os

# Add the parent directory to sys.path to allow imports from .app
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.database.connection import engine, Base
from sqlalchemy import inspect

def check_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in DB: {tables}")
    
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"Columns in {table}: {columns}")

if __name__ == "__main__":
    try:
        check_db()
    except Exception as e:
        print(f"Error: {e}")
