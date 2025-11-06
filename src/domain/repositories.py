"""Contratos de repositorio para acceder y persistir entidades del dominio."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import ChatMessage, Product


class IProductRepository(ABC):
    """Interfaz que declara las operaciones de persistencia de productos."""

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos disponibles en el catálogo.

        Returns:
            List[Product]: Colección completa de entidades ``Product``.
        """

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca un producto por su identificador.

        Args:
            product_id (int): Identificador único del producto.

        Returns:
            Optional[Product]: Entidad encontrada o ``None`` si no existe.
        """

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """Recupera productos filtrados por marca.

        Args:
            brand (str): Nombre de la marca a consultar.

        Returns:
            List[Product]: Lista de productos pertenecientes a la marca.
        """

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Recupera productos filtrados por categoría.

        Args:
            category (str): Categoría de producto a buscar.

        Returns:
            List[Product]: Productos que coinciden con la categoría solicitada.
        """

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Persiste un producto insertándolo o actualizándolo según corresponda.

        Args:
            product (Product): Entidad a guardar.

        Returns:
            Product: Entidad almacenada con los datos persistidos.
        """

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si el registro existía y fue eliminado.
        """


class IChatRepository(ABC):
    """Interfaz para manejar la persistencia del historial conversacional."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje y lo retorna tras su almacenamiento.

        Args:
            message (ChatMessage): Mensaje que se desea persistir.

        Returns:
            ChatMessage: Entidad almacenada con sus metadatos actualizados.
        """

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Obtiene el historial ordenado de una sesión.

        Args:
            session_id (str): Identificador de la conversación.
            limit (Optional[int]): Cantidad máxima de registros a retornar.

        Returns:
            List[ChatMessage]: Mensajes ordenados cronológicamente.
        """

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes asociados a una sesión.

        Args:
            session_id (str): Identificador de la conversación.

        Returns:
            int: Número de registros eliminados.
        """

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los mensajes más recientes de una sesión.

        Args:
            session_id (str): Conversación objetivo.
            count (int): Cantidad de mensajes a recuperar.

        Returns:
            List[ChatMessage]: Mensajes ordenados del más antiguo al más nuevo.
        """
