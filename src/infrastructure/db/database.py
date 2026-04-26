from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

# Motor de conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necesario para SQLite con FastAPI
)

# Factory de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Clase base para todos los modelos ORM
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency de FastAPI.
    Abre una sesión, la cede al endpoint y la cierra al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Crea todas las tablas definidas en los modelos ORM.
    Debe llamarse al arrancar la aplicación.
    """
    Base.metadata.create_all(bind=engine)