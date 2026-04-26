from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Implementación concreta del repositorio de chat con SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Helpers de conversión                                               #
    # ------------------------------------------------------------------ #

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM a entidad de dominio"""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad de dominio a modelo ORM"""
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )

    # ------------------------------------------------------------------ #
    #  Métodos del contrato                                                #
    # ------------------------------------------------------------------ #

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Persiste un mensaje y retorna la entidad con ID asignado"""
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Retorna el historial completo en orden cronológico.
        Si limit está definido, retorna solo los últimos N mensajes.
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.asc())
        )

        if limit is not None:
            # Toma los últimos N inviriendo el orden, luego restaura cronológico
            models = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            models.reverse()
        else:
            models = query.all()

        return [self._model_to_entity(m) for m in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión.
        Retorna la cantidad de mensajes eliminados.
        """
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Retorna los últimos N mensajes en orden cronológico.
        Crucial para construir el ChatContext correctamente.
        """
        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        models.reverse()  # De más antiguo a más reciente
        return [self._model_to_entity(m) for m in models]