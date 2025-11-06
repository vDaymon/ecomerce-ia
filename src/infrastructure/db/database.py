"""Utilidades de configuración de base de datos usando SQLAlchemy ORM."""
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Proporciona una sesión de base de datos para el ciclo de vida de la petición.

    Yields:
        Session: Sesión lista para interactuar con la base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inicializa el esquema y carga los datos iniciales."""
    from . import models  # noqa: F401 - ensure models are registered
    from .init_data import load_initial_data

    Base.metadata.create_all(bind=engine)
    load_initial_data()
