"""Aplicación FastAPI que expone los endpoints de e-commerce y chat."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
    title="E-commerce Chat IA",
    description="API para gestionar productos y chat conversacional con IA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Inicializa la base de datos y carga datos semilla al arrancar el servicio."""
    init_db()


@app.get("/")
def root() -> dict:
    """Retorna metadatos básicos del servicio.

    Returns:
        dict: Información mínima para verificación rápida del API.
    """
    return {
        "name": "E-commerce Chat IA",
        "version": "1.0.0",
        "endpoints": [
            "/products",
            "/products/{product_id}",
            "/chat",
            "/chat/history/{session_id}",
            "/health",
        ],
    }


@app.get("/health")
def health_check() -> dict:
    """Entrega un payload de verificación del estado del servicio.

    Returns:
        dict: Estado actual y marca temporal del sistema.
    """
    return {"status": "ok", "timestamp": datetime.utcnow()}


@app.get("/products", response_model=List[ProductDTO])
def list_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """Retorna el catálogo completo de productos.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[ProductDTO]: Listado de productos disponibles.
    """
    product_service = ProductService(SQLProductRepository(db))
    products = product_service.get_all_products()
    return [ProductDTO.model_validate(product) for product in products]


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto específico por identificador.

    Args:
        product_id (int): Identificador numérico del producto.
        db (Session): Sesión de base de datos inyectada.

    Returns:
        ProductDTO: Producto encontrado en el catálogo.

    Raises:
        HTTPException: Con código 404 si el producto no existe.
    """
    product_service = ProductService(SQLProductRepository(db))
    try:
        product = product_service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProductDTO.model_validate(product)


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat_endpoint(request: ChatMessageRequestDTO, db: Session = Depends(get_db)) -> ChatMessageResponseDTO:
    """Procesa un mensaje de chat y retorna la respuesta del asistente.

    Args:
        request (ChatMessageRequestDTO): Mensaje ingresado por el cliente.
        db (Session): Sesión de base de datos inyectada.

    Returns:
        ChatMessageResponseDTO: Respuesta generada por la IA.

    Raises:
        HTTPException: Con código 500 si ocurre un error en el servicio de chat.
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    chat_service = ChatService(product_repo, chat_repo, ai_service)

    try:
        return await chat_service.process_message(request)
    except ChatServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(session_id: str, limit: int = 10, db: Session = Depends(get_db)) -> List[ChatHistoryDTO]:
    """Recupera el historial de chat para una sesión determinada.

    Args:
        session_id (str): Identificador de la sesión de chat.
        limit (int): Máximo de mensajes a retornar.
        db (Session): Sesión de base de datos inyectada.

    Returns:
        List[ChatHistoryDTO]: Mensajes ordenados cronológicamente.
    """
    chat_repo = SQLChatRepository(db)
    product_repo = SQLProductRepository(db)
    chat_service = ChatService(product_repo, chat_repo, GeminiService())
    return chat_service.get_session_history(session_id, limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina el historial completo de una sesión.

    Args:
        session_id (str): Identificador de la sesión objetivo.
        db (Session): Sesión de base de datos inyectada.

    Returns:
        dict: Resultado con la cantidad de mensajes eliminados.
    """
    chat_repo = SQLChatRepository(db)
    deleted = chat_repo.delete_session_history(session_id)
    return {"session_id": session_id, "deleted_messages": deleted}
