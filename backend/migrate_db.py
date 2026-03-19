from app.database.connection import engine
from sqlalchemy import text

def migrate():
    print("🚀 Starting database migration...")
    try:
        with engine.connect() as connection:
            # Add column 'rol'
            print("Adding 'rol' column to 'docentes' table...")
            connection.execute(text("ALTER TABLE docentes ADD COLUMN rol VARCHAR(20) DEFAULT 'docente'"))
            connection.commit()
            print("✅ Column 'rol' added successfully!")
            
            # Optional: Set an admin user if you have one
            # connection.execute(text("UPDATE docentes SET rol = 'admin' WHERE email = 'your-admin@email.com'"))
            # connection.commit()
            
    except Exception as e:
        if "Duplicate column name" in str(e) or "1060" in str(e):
            print("ℹ️ Column 'rol' already exists.")
        else:
            print(f"❌ Migration error: {str(e)}")

if __name__ == "__main__":
    migrate()
