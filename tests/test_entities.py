"""Unit tests for domain entities verifying business invariants."""
from datetime import datetime
import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


def test_product_validation_errors() -> None:
    with pytest.raises(ValueError):
        Product(
            id=None,
            name="",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="",
        )

    with pytest.raises(ValueError):
        Product(
            id=None,
            name="Air Zoom",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=0,
            stock=5,
            description="",
        )

    with pytest.raises(ValueError):
        Product(
            id=None,
            name="Air Zoom",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=-1,
            description="",
        )


def test_product_stock_operations() -> None:
    product = Product(
        id=1,
        name="Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="",
    )

    assert product.is_available()

    product.reduce_stock(2)
    assert product.stock == 3

    with pytest.raises(ValueError):
        product.reduce_stock(0)

    with pytest.raises(ValueError):
        product.reduce_stock(10)

    product.increase_stock(5)
    assert product.stock == 8

    with pytest.raises(ValueError):
        product.increase_stock(0)


def test_chat_message_validation_and_roles() -> None:
    timestamp = datetime.utcnow()
    message = ChatMessage(id=None, session_id="abc", role="user", message="Hola", timestamp=timestamp)

    assert message.is_from_user()
    assert not message.is_from_assistant()

    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="", role="user", message="Hola", timestamp=timestamp)

    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="abc", role="user", message=" ", timestamp=timestamp)

    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="abc", role="bot", message="Hola", timestamp=timestamp)


def test_chat_context_formatting() -> None:
    timestamp = datetime.utcnow()
    messages = [
        ChatMessage(id=None, session_id="abc", role="user", message="Hola", timestamp=timestamp),
        ChatMessage(id=None, session_id="abc", role="assistant", message="Hola, ¿en qué puedo ayudarte?", timestamp=timestamp),
    ]
    context = ChatContext(messages=messages, max_messages=2)

    recent = context.get_recent_messages()
    assert recent == messages

    formatted = context.format_for_prompt()
    assert "Usuario: Hola" in formatted
    assert "Asistente: Hola, ¿en qué puedo ayudarte?" in formatted
