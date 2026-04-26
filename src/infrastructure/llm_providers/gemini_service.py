import os
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv

from src.domain.entities import Product
from src.domain.entities import ChatContext

load_dotenv()

SYSTEM_PROMPT = """
Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

INSTRUCCIONES:
- Sé amigable y profesional
- Usa el contexto de la conversación anterior
- Recomienda productos específicos cuando sea apropiado
- Menciona precios, tallas y disponibilidad
- Si un producto está agotado (stock 0), indícalo claramente
- Si no tienes información, sé honesto
- Responde siempre en español
"""


class GeminiService:
    """
    Servicio de IA que se comunica con la API de Gemini.
    Genera respuestas contextuales basadas en el catálogo y el historial.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def format_products_info(self, products: List[Product]) -> str:
        """Convierte la lista de productos a texto legible para el prompt"""
        if not products:
            return "No hay productos disponibles en este momento."

        lines = ["PRODUCTOS DISPONIBLES:\n"]
        for p in products:
            availability = f"Stock: {p.stock}" if p.stock > 0 else "AGOTADO"
            lines.append(
                f"- {p.name} | {p.brand} | Categoría: {p.category} "
                f"| Talla: {p.size} | Color: {p.color} "
                f"| Precio: ${p.price:.2f} | {availability}"
            )
        return "\n".join(lines)

    def _build_prompt(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """Ensambla el prompt completo con productos, historial y mensaje"""
        parts = []

        # Catálogo de productos
        parts.append(self.format_products_info(products))

        # Historial de conversación
        history = context.format_for_prompt()
        if history:
            parts.append(f"HISTORIAL DE CONVERSACIÓN:\n{history}")

        # Mensaje actual
        parts.append(f"Usuario: {user_message}\n\nAsistente:")

        return "\n\n".join(parts)

    # ------------------------------------------------------------------ #
    #  Método principal                                                    #
    # ------------------------------------------------------------------ #

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta de IA basada en el mensaje, productos y contexto.
        """
        try:
            prompt = self._build_prompt(user_message, products, context)
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()

        except Exception as e:
            raise RuntimeError(f"Error al llamar a Gemini API: {str(e)}") from e