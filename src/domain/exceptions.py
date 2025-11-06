"""Excepciones de dominio que representan reglas de negocio incumplidas."""

class ProductNotFoundError(Exception):
    """Error lanzado cuando no se encuentra un producto solicitado."""

    def __init__(self, product_id: int | None = None) -> None:
        """Inicializa la excepción con un mensaje específico.

        Args:
            product_id (Optional[int]): Identificador del producto buscado.
        """

        if product_id is not None:
            message = f"Producto con ID {product_id} no encontrado"
        else:
            message = "Producto no encontrado"
        super().__init__(message)


class InvalidProductDataError(Exception):
    """Error lanzado cuando los datos del producto son inválidos."""

    def __init__(self, message: str = "Datos de producto inválidos") -> None:
        """Inicializa la excepción con un detalle descriptivo del problema.

        Args:
            message (str): Explicación del error detectado.
        """

        super().__init__(message)


class ChatServiceError(Exception):
    """Error lanzado ante fallas controladas del servicio de chat."""

    def __init__(self, message: str = "Error en el servicio de chat") -> None:
        """Inicializa la excepción con el mensaje correspondiente.

        Args:
            message (str): Descripción del error ocurrido.
        """

        super().__init__(message)
