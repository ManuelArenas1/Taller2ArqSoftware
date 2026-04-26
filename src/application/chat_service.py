from datetime import datetime
from typing import List, Optional

from src.domain.entities import ChatMessage
from src.domain.entities import ChatContext
from src.domain.repositories import IChatRepository
from src.domain.repositories import IProductRepository
from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from src.infrastructure.llm_providers.gemini_service import GeminiService


class ChatServiceError(Exception):
    """Error general del servicio de chat"""
    pass


class ChatService:
    """
    Servicio de aplicación para el chat con IA.
    Orquesta el historial, el catálogo y la llamada a Gemini.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        gemini_service: GeminiService,
    ):
        self._product_repo = product_repository
        self._chat_repo = chat_repository
        self._gemini = gemini_service

    # ------------------------------------------------------------------ #
    #  Helpers privados                                                    #
    # ------------------------------------------------------------------ #

    def _save_message(self, session_id: str, role: str, message: str) -> ChatMessage:
        """Crea y persiste un ChatMessage"""
        chat_message = ChatMessage(
            id=None,
            session_id=session_id,
            role=role,
            message=message,
            timestamp=datetime.utcnow(),
        )
        return self._chat_repo.save_message(chat_message)

    # ------------------------------------------------------------------ #
    #  Método principal                                                    #
    # ------------------------------------------------------------------ #

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Flujo completo:
        1. Obtener historial reciente
        2. Obtener catálogo de productos
        3. Construir contexto
        4. Llamar a Gemini
        5. Persistir ambos mensajes
        6. Retornar DTO de respuesta
        """
        try:
            # 1. Historial reciente (últimos 6 mensajes)
            recent = self._chat_repo.get_recent_messages(request.session_id, count=6)

            # 2. Catálogo completo
            products = self._product_repo.get_all()

            # 3. Construir contexto conversacional
            context = ChatContext(messages=recent)

            # 4. Llamar a Gemini
            assistant_reply = await self._gemini.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            # 5. Persistir ambos mensajes
            self._save_message(request.session_id, "user", request.message)
            self._save_message(request.session_id, "assistant", assistant_reply)

            # 6. Retornar respuesta
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_reply,
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            raise ChatServiceError(f"Error al procesar el mensaje: {str(e)}") from e

    # ------------------------------------------------------------------ #
    #  Métodos adicionales                                                 #
    # ------------------------------------------------------------------ #

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """Retorna el historial de una sesión como lista de DTOs"""
        messages = self._chat_repo.get_session_history(session_id, limit=limit)
        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """Elimina todo el historial de una sesión, retorna cantidad eliminada"""
        return self._chat_repo.delete_session_history(session_id)