# database/connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

SQLSERVER_URL = os.getenv(
    "SQLSERVER_URL",
    "mssql+pyodbc://localhost?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&database=P1SW"
)

engine = create_engine(SQLSERVER_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

class DBExecutor:
    def __init__(self, engine):
        self.engine = engine

    def execute_non_query(self, query: str):
        with self.engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()

# Instancia global para usar en migrate
db = DBExecutor(engine)

