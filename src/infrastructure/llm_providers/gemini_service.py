"""Servicio de IA basado en Gemini que aprovecha los modelos generativos de Google."""
from __future__ import annotations

import os
from typing import Iterable, List

import google.generativeai as genai

from src.domain.entities import ChatContext, Product


class GeminiService:
    """Fachada sobre Google Gemini para generar respuestas contextuales."""

    def __init__(self, model_name: str = "gemini-2.0-flash") -> None:
        """Configura el modelo de Gemini a utilizar.

        Args:
            model_name (str): Nombre del modelo generativo a invocar.

        Raises:
            ValueError: Si la variable de entorno ``GEMINI_API_KEY`` no está definida.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno")

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    async def generate_response(self, user_message: str, products: List[Product], context: ChatContext) -> str:
        """Genera una respuesta contextual usando Gemini.

        Args:
            user_message (str): Mensaje ingresado por el usuario.
            products (List[Product]): Catálogo disponible durante la conversación.
            context (ChatContext): Historial de mensajes recientes.

        Returns:
            str: Respuesta generada por el modelo de IA.
        """
        prompt = self._build_prompt(user_message, products, context)
        response = await self._model.generate_content_async(prompt)
        if not response.candidates:
            return "Lo siento, no tengo información suficiente en este momento."
        return response.text

    def _build_prompt(self, user_message: str, products: Iterable[Product], context: ChatContext) -> str:
        """Construye el prompt completo que se enviará al modelo de IA.

        Args:
            user_message (str): Mensaje más reciente del usuario.
            products (Iterable[Product]): Productos disponibles para recomendar.
            context (ChatContext): Historial resumido de la conversación.

        Returns:
            str: Prompt en texto plano listo para el modelo generativo.
        """
        products_info = self._format_products_info(products)
        context_prompt = context.format_for_prompt()

        return (
            "Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
            "Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
            "PRODUCTOS DISPONIBLES:\n"
            f"{products_info}\n\n"
            "INSTRUCCIONES:\n"
            "- Sé amigable y profesional\n"
            "- Usa el contexto de la conversación anterior\n"
            "- Recomienda productos específicos cuando sea apropiado\n"
            "- Menciona precios, tallas y disponibilidad\n"
            "- Si no tienes información, sé honesto\n\n"
            f"Historial reciente:\n{context_prompt}\n\n"
            f"Usuario: {user_message}\n\n"
            "Asistente:"
        )

    def _format_products_info(self, products: Iterable[Product]) -> str:
        """Formatea la información de productos para el prompt.

        Args:
            products (Iterable[Product]): Productos a describir.

        Returns:
            str: Texto con cada producto en una línea.
        """
        lines = []
        for product in products:
            availability = "Disponible" if product.is_available() else "Agotado"
            lines.append(
                f"- {product.name} | Marca: {product.brand} | Categoría: {product.category} | "
                f"Talla: {product.size} | Color: {product.color} | Precio: ${product.price:.2f} | "
                f"Stock: {product.stock} ({availability})"
            )
        return "\n".join(lines) if lines else "No hay productos disponibles actualmente."
