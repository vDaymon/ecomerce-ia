"""Servicio de aplicación responsable de orquestar las interacciones de chat."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Protocol

from src.domain.entities import ChatContext, ChatMessage, Product
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository

from .dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO


class AIServiceProtocol(Protocol):
    """Contrato tipado para los proveedores de IA consumidos por el servicio."""

    async def generate_response(self, user_message: str, products: List[Product], context: ChatContext) -> str:
        """Genera una respuesta del asistente usando el contexto disponible.

        Args:
            user_message (str): Mensaje recibido por parte del usuario.
            products (List[Product]): Catálogo actual para enriquecer la respuesta.
            context (ChatContext): Historial reciente que aporta memoria conversacional.

        Returns:
            str: Respuesta redactada por el proveedor de IA.
        """


class ChatService:
    """Orquesta los flujos conversacionales con el asistente de IA.

    Attributes:
        _product_repo (IProductRepository): Repositorio para productos.
        _chat_repo (IChatRepository): Repositorio para historial de chat.
        _ai_service (AIServiceProtocol): Servicio de IA que genera respuestas.
        _context_size (int): Cantidad máxima de mensajes a usar como contexto.
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        chat_repo: IChatRepository,
        ai_service: AIServiceProtocol,
        context_size: int = 6,
    ) -> None:
        """Inicializa el servicio con los repositorios y proveedor de IA.

        Args:
            product_repo (IProductRepository): Repositorio de productos.
            chat_repo (IChatRepository): Repositorio de historial de chat.
            ai_service (AIServiceProtocol): Servicio capaz de generar respuestas.
            context_size (int): Cantidad máxima de mensajes a considerar.
        """
        self._product_repo = product_repo
        self._chat_repo = chat_repo
        self._ai_service = ai_service
        self._context_size = context_size

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """Procesa un mensaje entrante, persiste el historial y retorna la respuesta.

        Args:
            request (ChatMessageRequestDTO): Mensaje enviado por el usuario.

        Returns:
            ChatMessageResponseDTO: Respuesta del asistente al usuario.

        Raises:
            ChatServiceError: Si ocurre algún problema en el flujo conversacional.
        """

        try:
            products = self._product_repo.get_all()
            history = self._chat_repo.get_recent_messages(request.session_id, self._context_size)
            context = ChatContext(messages=history, max_messages=self._context_size)

            ai_response = await self._ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            user_timestamp = datetime.utcnow()
            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=user_timestamp,
            )
            self._chat_repo.save_message(user_message)

            assistant_timestamp = datetime.utcnow()
            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=ai_response,
                timestamp=assistant_timestamp,
            )
            self._chat_repo.save_message(assistant_message)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_response,
                timestamp=assistant_timestamp,
            )
        except Exception as exc:  # pragma: no cover - defensive catch
            raise ChatServiceError(str(exc)) from exc

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatHistoryDTO]:
        """Recupera el historial de conversación de una sesión.

        Args:
            session_id (str): Identificador de la sesión de chat.
            limit (Optional[int]): Número máximo de mensajes a retornar.

        Returns:
            List[ChatHistoryDTO]: Mensajes ordenados listos para exponer al cliente.
        """
        messages = self._chat_repo.get_session_history(session_id, limit)
        return [ChatHistoryDTO.model_validate(message) for message in messages]

    def clear_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes guardados de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self._chat_repo.delete_session_history(session_id)
