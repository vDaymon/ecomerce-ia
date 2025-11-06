"""Repositorio de chat respaldado por SQLAlchemy que gestiona el historial."""
from __future__ import annotations

from typing import List

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository

from ..db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """Repositorio concreto para persistir mensajes del chat."""

    def __init__(self, db_session: Session) -> None:
        """Inicializa el repositorio con una sesión de base de datos.

        Args:
            db_session (Session): Sesión de SQLAlchemy activa.
        """
        self._db = db_session

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Mapea un modelo ORM a entidad de dominio."""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Transforma una entidad de dominio en modelo ORM."""
        if entity.id is not None:
            model = self._db.query(ChatMemoryModel).filter(ChatMemoryModel.id == entity.id).first()
            if model is None:
                model = ChatMemoryModel(id=entity.id)
        else:
            model = ChatMemoryModel()

        model.session_id = entity.session_id
        model.role = entity.role
        model.message = entity.message
        model.timestamp = entity.timestamp
        return model

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de chat y retorna la entidad persistida."""
        model = self._entity_to_model(message)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: int | None = None) -> List[ChatMessage]:
        """Recupera el historial completo de una sesión.

        Args:
            session_id (str): Identificador de la conversación.
            limit (Optional[int]): Máximo de registros a retornar.

        Returns:
            List[ChatMessage]: Mensajes ordenados ascendentemente por fecha.
        """
        query = self._db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id).order_by(asc(ChatMemoryModel.timestamp))
        if limit is not None:
            query = query.limit(limit)
        return [self._model_to_entity(model) for model in query.all()]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes de una sesión específica.

        Args:
            session_id (str): Identificador de la conversación.

        Returns:
            int: Cantidad de registros eliminados.
        """
        deleted = (
            self._db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete(synchronize_session=False)
        )
        self._db.commit()
        return int(deleted)

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los mensajes más recientes de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de la conversación.
            count (int): Cantidad de mensajes recientes a recuperar.

        Returns:
            List[ChatMessage]: Mensajes ordenados del más antiguo al más reciente.
        """
        query = (
            self._db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(desc(ChatMemoryModel.timestamp))
            .limit(count)
        )
        models = list(query.all())
        models.reverse()
        return [self._model_to_entity(model) for model in models]
