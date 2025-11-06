"""Unit tests for application services using simple fakes."""
import asyncio
from datetime import datetime
from typing import List

import pytest

from src.application.chat_service import AIServiceProtocol, ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.domain.repositories import IChatRepository, IProductRepository


class InMemoryProductRepository(IProductRepository):
    """In-memory fake repository for product tests."""

    def __init__(self, products: List[Product] | None = None) -> None:
        self.products = products or []

    def get_all(self) -> List[Product]:
        return list(self.products)

    def get_by_id(self, product_id: int) -> Product | None:
        return next((product for product in self.products if product.id == product_id), None)

    def get_by_brand(self, brand: str) -> List[Product]:
        return [product for product in self.products if product.brand.lower() == brand.lower()]

    def get_by_category(self, category: str) -> List[Product]:
        return [product for product in self.products if product.category.lower() == category.lower()]

    def save(self, product: Product) -> Product:
        if product.id is None:
            product.id = max((p.id or 0 for p in self.products), default=0) + 1
            self.products.append(product)
        else:
            self.products = [product if p.id == product.id else p for p in self.products]
        return product

    def delete(self, product_id: int) -> bool:
        original_len = len(self.products)
        self.products = [product for product in self.products if product.id != product_id]
        return len(self.products) != original_len


class InMemoryChatRepository(IChatRepository):
    """In-memory fake repository for chat tests."""

    def __init__(self) -> None:
        self.messages: List[ChatMessage] = []

    def save_message(self, message: ChatMessage) -> ChatMessage:
        message.id = len(self.messages) + 1
        self.messages.append(message)
        return message

    def get_session_history(self, session_id: str, limit: int | None = None) -> List[ChatMessage]:
        history = [msg for msg in self.messages if msg.session_id == session_id]
        history.sort(key=lambda msg: msg.timestamp)
        if limit is not None:
            history = history[:limit]
        return history

    def delete_session_history(self, session_id: str) -> int:
        original_len = len(self.messages)
        self.messages = [msg for msg in self.messages if msg.session_id != session_id]
        return original_len - len(self.messages)

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        history = [msg for msg in self.messages if msg.session_id == session_id]
        history.sort(key=lambda msg: msg.timestamp)
        return history[-count:]


class FakeAIService(AIServiceProtocol):
    """Fake AI service returning deterministic responses."""

    async def generate_response(self, user_message: str, products: List[Product], context):
        if "fallo" in user_message:
            raise RuntimeError("AI error")
        return "Respuesta generada"


@pytest.fixture()
def sample_products() -> List[Product]:
    return [
        Product(id=1, name="Air Zoom", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=5, description=""),
        Product(id=2, name="Ultraboost", brand="Adidas", category="Running", size="41", color="Blanco", price=150.0, stock=3, description=""),
    ]


def test_product_service_crud(sample_products: List[Product]) -> None:
    repo = InMemoryProductRepository(sample_products)
    service = ProductService(repo)

    all_products = service.get_all_products()
    assert len(all_products) == 2

    product = service.get_product_by_id(1)
    assert product.name == "Air Zoom"

    new_product_dto = ProductDTO(name="Suede", brand="Puma", category="Casual", size="40", color="Azul", price=80.0, stock=10, description="")
    created = service.create_product(new_product_dto)
    assert created.id is not None
    assert len(service.get_all_products()) == 3

    updated_dto = ProductDTO(name="Air Zoom Updated", brand="Nike", category="Running", size="42", color="Negro", price=130.0, stock=5, description="")
    updated = service.update_product(1, updated_dto)
    assert updated.name == "Air Zoom Updated"

    service.delete_product(2)
    assert len(service.get_all_products()) == 2

    with pytest.raises(ProductNotFoundError):
        service.get_product_by_id(99)


def test_chat_service_flow(sample_products: List[Product]) -> None:
    product_repo = InMemoryProductRepository(sample_products)
    chat_repo = InMemoryChatRepository()
    ai_service = FakeAIService()
    service = ChatService(product_repo, chat_repo, ai_service)

    request = ChatMessageRequestDTO(session_id="abc", message="Hola")
    response = asyncio.run(service.process_message(request))

    assert response.assistant_message == "Respuesta generada"
    history = chat_repo.get_session_history("abc")
    assert len(history) == 2


def test_chat_service_handles_ai_errors(sample_products: List[Product]) -> None:
    product_repo = InMemoryProductRepository(sample_products)
    chat_repo = InMemoryChatRepository()
    ai_service = FakeAIService()
    service = ChatService(product_repo, chat_repo, ai_service)

    request = ChatMessageRequestDTO(session_id="abc", message="Provoca fallo")
    with pytest.raises(ChatServiceError):
        asyncio.run(service.process_message(request))


def test_chat_service_history_management(sample_products: List[Product]) -> None:
    product_repo = InMemoryProductRepository(sample_products)
    chat_repo = InMemoryChatRepository()
    ai_service = FakeAIService()
    service = ChatService(product_repo, chat_repo, ai_service)

    timestamp = datetime.utcnow()
    chat_repo.save_message(ChatMessage(id=None, session_id="abc", role="user", message="Hola", timestamp=timestamp))
    chat_repo.save_message(ChatMessage(id=None, session_id="abc", role="assistant", message="Hola", timestamp=timestamp))

    history_dtos = service.get_session_history("abc")
    assert len(history_dtos) == 2

    deleted = service.clear_session_history("abc")
    assert deleted == 2
    assert service.get_session_history("abc") == []
