"""Entidades de dominio que encapsulan las reglas de negocio del e-commerce."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Product:
    """Entidad que representa un producto del catálogo.

    Esta entidad concentra las reglas de negocio asociadas con los productos,
    incluyendo validaciones de precio y stock necesarias para garantizar que el
    inventario se mantenga consistente.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre comercial del producto.
        brand (str): Marca a la que pertenece el producto.
        category (str): Categoría principal (Running, Casual, etc.).
        size (str): Talla disponible descrita como cadena.
        color (str): Color predominante del producto.
        price (float): Precio unitario en USD.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripción corta para el usuario final.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """Valida las invariantes principales tras la inicialización.

        Raises:
            ValueError: Si el nombre está vacío, el precio es menor o igual a
                cero, o el stock es negativo.
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        if self.price <= 0:
            raise ValueError("El precio del producto debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock del producto no puede ser negativo")

    def is_available(self) -> bool:
        """Indica si el producto cuenta con stock disponible.

        Returns:
            bool: ``True`` cuando el stock es mayor a cero, ``False`` en caso
                contrario.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Disminuye el stock verificando que la operación sea válida.

        Args:
            quantity (int): Cantidad de unidades a descontar.

        Raises:
            ValueError: Si la cantidad es menor o igual a cero o supera el
                stock disponible.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError("Stock insuficiente para completar la operación")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Incrementa el stock con una cantidad válida.

        Args:
            quantity (int): Cantidad de unidades a agregar.

        Raises:
            ValueError: Si la cantidad es menor o igual a cero.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad que modela un mensaje dentro de una sesión de chat.

    Attributes:
        id (Optional[int]): Identificador opcional del mensaje.
        session_id (str): Identificador de la conversación a la que pertenece.
        role (str): Rol del emisor (``"user"`` o ``"assistant"``).
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Marca de tiempo de la creación del mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str  # 'user' or 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """Valida la estructura básica del mensaje.

        Raises:
            ValueError: Si ``session_id`` o ``message`` están vacíos o si el
                rol no es uno de los valores permitidos.
        """
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        if self.role not in {"user", "assistant"}:
            raise ValueError("El rol debe ser 'user' o 'assistant'")

    def is_from_user(self) -> bool:
        """Verifica si el mensaje fue enviado por el usuario final.

        Returns:
            bool: ``True`` cuando el rol es ``"user"``.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """Indica si el mensaje fue emitido por el asistente de IA.

        Returns:
            bool: ``True`` cuando el rol es ``"assistant"``.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Objeto de valor que conserva el historial relevante de una sesión.

    Attributes:
        messages (List[ChatMessage]): Colección de mensajes registrados.
        max_messages (int): Número máximo de mensajes a considerar en contexto.
    """

    messages: List[ChatMessage] = field(default_factory=list)
    max_messages: int = 6

    def get_recent_messages(self) -> List[ChatMessage]:
        """Obtiene los mensajes más recientes respetando el límite definido.

        Returns:
            List[ChatMessage]: Lista cronológica de mensajes recientes.
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """Genera una transcripción legible para enviar al modelo de IA.

        Returns:
            str: Texto con la conversación formateada para el prompt.
        """
        formatted_lines: List[str] = []
        for message in self.get_recent_messages():
            prefix = "Usuario" if message.is_from_user() else "Asistente"
            formatted_lines.append(f"{prefix}: {message.message}")
        return "\n".join(formatted_lines)
