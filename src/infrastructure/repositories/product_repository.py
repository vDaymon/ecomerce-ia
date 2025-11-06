"""Implementación de repositorio de productos respaldada por SQLAlchemy."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository

from ..db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """Repositorio concreto que persiste productos usando sesiones de SQLAlchemy."""

    def __init__(self, db_session: Session) -> None:
        """Inicializa el repositorio con una sesión activa.

        Args:
            db_session (Session): Sesión de SQLAlchemy.
        """
        self._db = db_session

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convierte un modelo ORM en entidad de dominio."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad de dominio en modelo ORM listo para persistir."""
        if entity.id is not None:
            model = self._db.query(ProductModel).filter(ProductModel.id == entity.id).first()
            if model is None:
                model = ProductModel(id=entity.id)
        else:
            model = ProductModel()

        model.name = entity.name
        model.brand = entity.brand
        model.category = entity.category
        model.size = entity.size
        model.color = entity.color
        model.price = entity.price
        model.stock = entity.stock
        model.description = entity.description
        return model

    def get_all(self) -> List[Product]:
        """Obtiene todos los productos almacenados.

        Returns:
            List[Product]: Entidades convertidas desde la base de datos.
        """
        return [self._model_to_entity(model) for model in self._db.query(ProductModel).all()]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca un producto por su identificador.

        Args:
            product_id (int): Identificador único del producto.

        Returns:
            Optional[Product]: Producto encontrado o ``None``.
        """
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos filtrados por marca (búsqueda insensible a mayúsculas).

        Args:
            brand (str): Nombre de la marca a buscar.

        Returns:
            List[Product]: Productos que pertenecen a la marca indicada.
        """
        models = self._db.query(ProductModel).filter(ProductModel.brand.ilike(brand)).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos filtrados por categoría.

        Args:
            category (str): Categoría objetivo.

        Returns:
            List[Product]: Productos que coinciden con la categoría.
        """
        models = self._db.query(ProductModel).filter(ProductModel.category.ilike(category)).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """Guarda (crea o actualiza) un producto.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad resultante después del commit.
        """
        model = self._entity_to_model(product)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si la operación fue exitosa.
        """
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
