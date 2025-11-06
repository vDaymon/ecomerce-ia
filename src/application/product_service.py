"""Servicio de aplicación que orquesta los casos de uso de productos."""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Optional

from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.domain.repositories import IProductRepository

from .dtos import ProductDTO


class ProductService:
    """Coordina las operaciones de negocio relacionadas con productos.

    Attributes:
        _product_repository (IProductRepository): Repositorio utilizado para
            acceder y persistir entidades ``Product``.
    """

    def __init__(self, product_repository: IProductRepository) -> None:
        """Inicializa el servicio con su dependencia de repositorio.

        Args:
            product_repository (IProductRepository): Implementación concreta
                para interactuar con la persistencia.
        """
        self._product_repository = product_repository

    def _dto_to_entity(self, dto: ProductDTO, product_id: Optional[int] = None) -> Product:
        """Convierte un DTO en una entidad ``Product``.

        Args:
            dto (ProductDTO): DTO con los datos a mapear.
            product_id (Optional[int]): Identificador existente a preservar.

        Returns:
            Product: Entidad lista para aplicarle reglas de negocio.
        """
        data = dto.model_dump()
        if product_id is not None:
            data["id"] = product_id
        return Product(**data)

    def get_all_products(self) -> List[Product]:
        """Recupera todos los productos del catálogo.

        Returns:
            List[Product]: Lista completa de productos.
        """
        return self._product_repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """Obtiene un producto por su identificador.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Product: Entidad encontrada.

        Raises:
            ProductNotFoundError: Cuando el producto no existe.
        """
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    def search_products(self, filters: Optional[Dict[str, object]] = None) -> List[Product]:
        """Busca productos aplicando filtros por marca, categoría o stock.

        Args:
            filters (Optional[Dict[str, object]]): Diccionario con filtros
                opcionales (``brand``, ``category``, ``available``).

        Returns:
            List[Product]: Productos que cumplen con los filtros aplicados.
        """
        filters = filters or {}
        brand = filters.get("brand")
        category = filters.get("category")
        require_available = bool(filters.get("available"))

        candidates: Iterable[Product]
        if brand and not category:
            candidates = self._product_repository.get_by_brand(str(brand))
        elif category and not brand:
            candidates = self._product_repository.get_by_category(str(category))
        else:
            candidates = self._product_repository.get_all()

        results = list(candidates)

        if brand and category:
            results = [product for product in results if product.brand.lower() == str(brand).lower() and product.category.lower() == str(category).lower()]

        if require_available:
            results = [product for product in results if product.is_available()]

        return results

    def create_product(self, product_dto: ProductDTO) -> Product:
        """Crea un producto nuevo aplicando las reglas del dominio.

        Args:
            product_dto (ProductDTO): Información del producto a crear.

        Returns:
            Product: Entidad persistida con su identificador asignado.
        """
        product_entity = self._dto_to_entity(product_dto)
        return self._product_repository.save(product_entity)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """Actualiza un producto existente verificando su existencia.

        Args:
            product_id (int): Identificador del producto a actualizar.
            product_dto (ProductDTO): Datos actualizados.

        Returns:
            Product: Entidad resultante después de la actualización.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        existing = self._product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)
        update_data = asdict(existing)
        update_data.update(product_dto.model_dump(exclude_unset=True))
        update_data["id"] = product_id
        updated_entity = Product(**update_data)
        return self._product_repository.save(updated_entity)

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si el producto fue eliminado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        if self._product_repository.get_by_id(product_id) is None:
            raise ProductNotFoundError(product_id)
        return self._product_repository.delete(product_id)

    def get_available_products(self) -> List[Product]:
        """Obtiene los productos que tienen stock disponible.

        Returns:
            List[Product]: Productos cuya cantidad en inventario es positiva.
        """
        return [product for product in self._product_repository.get_all() if product.is_available()]
