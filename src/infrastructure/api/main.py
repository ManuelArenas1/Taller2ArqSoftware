# src/infrastructure/api/main.py

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.db.init_data import load_initial_data
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.product_service import ProductService, ProductNotFoundError
from src.application.chat_service import ChatService, ChatServiceError
from src.application.dtos import ProductDTO
from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)


# ------------------------------------------------------------------ #
#  Inicialización                                                      #
# ------------------------------------------------------------------ #

app = FastAPI(
    title="E-Commerce Chat AI",
    description="API para e-commerce de zapatos con asistente de IA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Inicializa la BD y carga datos al arrancar la aplicación"""
    init_db()
    load_initial_data()


# ------------------------------------------------------------------ #
#  Helpers de dependencias                                             #
# ------------------------------------------------------------------ #

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(SQLProductRepository(db))


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(
        product_repository=SQLProductRepository(db),
        chat_repository=SQLChatRepository(db),
        gemini_service=GeminiService(),
    )


# ------------------------------------------------------------------ #
#  Endpoints generales                                                 #
# ------------------------------------------------------------------ #

@app.get("/")
def root():
    """Información básica de la API"""
    return {
        "name": "E-Commerce Chat AI",
        "version": "1.0.0",
        "description": "API para e-commerce de zapatos con asistente de IA",
        "endpoints": {
            "products": "/products",
            "chat": "/chat",
            "docs": "/docs",
            "health": "/health",
        },
    }


@app.get("/health")
def health_check():
    """Verifica que la API esté operativa"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ------------------------------------------------------------------ #
#  Endpoints de productos                                              #
# ------------------------------------------------------------------ #

@app.get("/products", response_model=List[ProductDTO])
def get_all_products(service: ProductService = Depends(get_product_service)):
    """Lista todos los productos del catálogo"""
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """Obtiene un producto por su ID"""
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")


# ------------------------------------------------------------------ #
#  Endpoints de chat                                                   #
# ------------------------------------------------------------------ #

@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat(
    request: ChatMessageRequestDTO,
    service: ChatService = Depends(get_chat_service),
):
    """Procesa un mensaje del usuario y retorna respuesta de la IA"""
    try:
        return await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = 10,
    service: ChatService = Depends(get_chat_service),
):
    """Obtiene el historial de mensajes de una sesión"""
    return service.get_session_history(session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
):
    """Elimina el historial completo de una sesión"""
    deleted = service.clear_session_history(session_id)
    return {
        "session_id": session_id,
        "messages_deleted": deleted,
    }