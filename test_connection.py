from database.connection import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DB_NAME()"))
            db_name = result.scalar()
            print(f"✅ Conectado a la base de datos: {db_name}")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == "__main__":
    test_connection()
