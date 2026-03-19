from app.database.connection import engine
from sqlalchemy import text

def test_db():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check if 'docentes' table exists
            result = connection.execute(text("SHOW TABLES LIKE 'docentes'"))
            if result.fetchone():
                print("✅ Table 'docentes' exists.")
                # Check columns
                result = connection.execute(text("DESCRIBE docentes"))
                cols = [row[0] for row in result.fetchall()]
                print(f"Columns in 'docentes': {cols}")
                if 'rol' not in cols:
                    print("❌ MISSING COLUMN: 'rol'. Run: ALTER TABLE docentes ADD COLUMN rol VARCHAR(20) DEFAULT 'docente';")
            else:
                print("❌ Table 'docentes' NOT FOUND.")
                
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

if __name__ == "__main__":
    test_db()
