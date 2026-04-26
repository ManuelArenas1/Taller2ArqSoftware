from datetime import datetime
from sqlalchemy import Integer, String, Float, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.database import Base


class ProductModel(Base):
    """Modelo ORM para la tabla de productos"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    size: Mapped[str] = mapped_column(String(20), nullable=True)
    color: Mapped[str] = mapped_column(String(50), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Índices para columnas de búsqueda frecuente
    __table_args__ = (
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
    )

    def __repr__(self):
        return f"<ProductModel id={self.id} name={self.name} brand={self.brand}>"


class ChatMemoryModel(Base):
    """Modelo ORM para el historial de conversaciones"""

    __tablename__ = "chat_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<ChatMemoryModel id={self.id} session={self.session_id} role={self.role}>"