"""Objetos de transferencia de datos utilizados en la capa de aplicación."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ProductDTO(BaseModel):
    """DTO que transporta información de productos entre capas.

    Attributes:
        id (Optional[int]): Identificador del producto.
        name (str): Nombre descriptivo del producto.
        brand (str): Marca a la que pertenece.
        category (str): Categoría o tipo.
        size (str): Talla disponible.
        color (str): Color principal.
        price (float): Precio de venta.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripción corta mostrada al usuario.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, value: float) -> float:
        """Valida que el precio sea estrictamente positivo.

        Args:
            value (float): Valor recibido para el precio.

        Returns:
            float: Valor validado del campo.

        Raises:
            ValueError: Si el precio es menor o igual a cero.
        """
        if value <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return value

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, value: int) -> int:
        """Valida que el stock sea mayor o igual a cero.

        Args:
            value (int): Cantidad disponible reportada.

        Returns:
            int: Valor validado del campo.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if value < 0:
            raise ValueError("El stock no puede ser negativo")
        return value

    class Config:
        from_attributes = True


class ChatMessageRequestDTO(BaseModel):
    """DTO que representa el mensaje de chat enviado por el cliente."""

    session_id: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, value: str) -> str:
        """Valida que el mensaje contenga caracteres visibles.

        Args:
            value (str): Texto ingresado por el usuario.

        Returns:
            str: Cadena validada.

        Raises:
            ValueError: Si el mensaje está vacío.
        """
        if not value or not value.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return value

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, value: str) -> str:
        """Valida que el identificador de sesión esté presente.

        Args:
            value (str): Identificador recibido.

        Returns:
            str: Identificador validado.

        Raises:
            ValueError: Si el identificador está vacío.
        """
        if not value or not value.strip():
            raise ValueError("El session_id no puede estar vacío")
        return value


class ChatMessageResponseDTO(BaseModel):
    """DTO que expone la respuesta generada por el asistente de IA."""

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO que entrega registros del historial de conversación."""

    id: int
    role: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True
