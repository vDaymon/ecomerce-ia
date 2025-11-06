"""Modelos ORM de SQLAlchemy que representan las entidades persistidas."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


class ProductModel(Base):
    """Modelo ORM que refleja la tabla ``products`` en la base de datos."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)


class ChatMemoryModel(Base):
    """Modelo ORM que almacena los registros del historial conversacional."""

    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
