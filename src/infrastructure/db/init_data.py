"""Utilidades para poblar la base de datos con datos iniciales del catálogo."""
from __future__ import annotations

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import ProductModel


def load_initial_data() -> None:
    """Carga datos semilla cuando la tabla de productos está vacía."""
    session: Session = SessionLocal()
    try:
        if session.query(ProductModel).count() > 0:
            return

        products = [
            ProductModel(
                name="Nike Air Zoom Pegasus",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=120.0,
                stock=5,
                description="Zapatillas de running con amortiguación reactiva.",
            ),
            ProductModel(
                name="Adidas Ultraboost",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=150.0,
                stock=3,
                description="Tecnología Boost para máxima comodidad.",
            ),
            ProductModel(
                name="Puma Suede Classic",
                brand="Puma",
                category="Casual",
                size="40",
                color="Azul",
                price=80.0,
                stock=10,
                description="Diseño retro con materiales premium.",
            ),
            ProductModel(
                name="New Balance 574",
                brand="New Balance",
                category="Casual",
                size="42",
                color="Gris",
                price=110.0,
                stock=8,
                description="Icono clásico de la marca con soporte adicional.",
            ),
            ProductModel(
                name="Reebok Nano X",
                brand="Reebok",
                category="Training",
                size="43",
                color="Verde",
                price=130.0,
                stock=6,
                description="Entrenamiento funcional con estabilidad mejorada.",
            ),
            ProductModel(
                name="Nike Air Force 1",
                brand="Nike",
                category="Casual",
                size="41",
                color="Blanco",
                price=95.0,
                stock=12,
                description="Clásico del streetwear con estilo atemporal.",
            ),
            ProductModel(
                name="Adidas Stan Smith",
                brand="Adidas",
                category="Casual",
                size="40",
                color="Verde",
                price=85.0,
                stock=9,
                description="Elegancia minimalista con detalles en verde icónico.",
            ),
            ProductModel(
                name="Asics Gel-Kayano",
                brand="Asics",
                category="Running",
                size="44",
                color="Azul Marino",
                price=160.0,
                stock=4,
                description="Soporte premium para corredores de larga distancia.",
            ),
            ProductModel(
                name="Clarks Desert Boot",
                brand="Clarks",
                category="Formal",
                size="42",
                color="Arena",
                price=140.0,
                stock=7,
                description="Bota elegante con suela de crepé tradicional.",
            ),
            ProductModel(
                name="Cole Haan Zerogrand",
                brand="Cole Haan",
                category="Formal",
                size="43",
                color="Negro",
                price=180.0,
                stock=5,
                description="Zapato formal ultraligero con amortiguación moderna.",
            ),
        ]

        session.add_all(products)
        session.commit()
    finally:
        session.close()