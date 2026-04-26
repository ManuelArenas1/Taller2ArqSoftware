# tests/test_entities.py

import pytest
from datetime import datetime
from src.domain.entities import Product
from src.domain.entities import ChatMessage
from src.domain.entities import ChatContext


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def valid_product():
    return Product(
        id=1,
        name="Air Max 270",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=150.00,
        stock=10,
        description="Zapatilla de running",
    )


@pytest.fixture
def user_message():
    return ChatMessage(
        id=1,
        session_id="session-001",
        role="user",
        message="Hola, busco zapatillas",
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def assistant_message():
    return ChatMessage(
        id=2,
        session_id="session-001",
        role="assistant",
        message="Hola, con gusto te ayudo",
        timestamp=datetime.utcnow(),
    )


# ------------------------------------------------------------------ #
#  Tests de Product — validaciones                                     #
# ------------------------------------------------------------------ #

class TestProductValidations:

    def test_price_zero_raises_error(self):
        with pytest.raises(ValueError, match="precio"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="42", color="Rojo", price=0, stock=5,
                    description="Test")

    def test_price_negative_raises_error(self):
        with pytest.raises(ValueError, match="precio"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="42", color="Rojo", price=-10.0, stock=5,
                    description="Test")

    def test_stock_negative_raises_error(self):
        with pytest.raises(ValueError, match="stock"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="42", color="Rojo", price=100.0, stock=-1,
                    description="Test")

    def test_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="nombre"):
            Product(id=None, name="", brand="X", category="Y",
                    size="42", color="Rojo", price=100.0, stock=5,
                    description="Test")

    def test_whitespace_name_raises_error(self):
        with pytest.raises(ValueError, match="nombre"):
            Product(id=None, name="   ", brand="X", category="Y",
                    size="42", color="Rojo", price=100.0, stock=5,
                    description="Test")

    def test_valid_product_creates_successfully(self, valid_product):
        assert valid_product.name == "Air Max 270"
        assert valid_product.price == 150.00
        assert valid_product.stock == 10

    def test_stock_zero_is_valid(self):
        """Stock en cero es válido — producto agotado pero existente"""
        product = Product(id=None, name="Test", brand="X", category="Y",
                          size="42", color="Rojo", price=100.0, stock=0,
                          description="Test")
        assert product.stock == 0


# ------------------------------------------------------------------ #
#  Tests de Product — métodos                                          #
# ------------------------------------------------------------------ #

class TestProductMethods:

    def test_is_available_with_stock(self, valid_product):
        assert valid_product.is_available() is True

    def test_is_available_without_stock(self, valid_product):
        valid_product.stock = 0
        assert valid_product.is_available() is False

    def test_reduce_stock_success(self, valid_product):
        valid_product.reduce_stock(3)
        assert valid_product.stock == 7

    def test_reduce_stock_all(self, valid_product):
        valid_product.reduce_stock(10)
        assert valid_product.stock == 0

    def test_reduce_stock_exceeds_raises_error(self, valid_product):
        with pytest.raises(ValueError, match="suficiente stock"):
            valid_product.reduce_stock(99)

    def test_reduce_stock_zero_raises_error(self, valid_product):
        with pytest.raises(ValueError, match="positiva"):
            valid_product.reduce_stock(0)

    def test_reduce_stock_negative_raises_error(self, valid_product):
        with pytest.raises(ValueError, match="positiva"):
            valid_product.reduce_stock(-5)

    def test_increase_stock_success(self, valid_product):
        valid_product.increase_stock(5)
        assert valid_product.stock == 15

    def test_increase_stock_zero_raises_error(self, valid_product):
        with pytest.raises(ValueError, match="positiva"):
            valid_product.increase_stock(0)

    def test_increase_stock_negative_raises_error(self, valid_product):
        with pytest.raises(ValueError, match="positiva"):
            valid_product.increase_stock(-3)


# ------------------------------------------------------------------ #
#  Tests de ChatMessage — validaciones                                 #
# ------------------------------------------------------------------ #

class TestChatMessageValidations:

    def test_invalid_role_raises_error(self):
        with pytest.raises(ValueError, match="rol"):
            ChatMessage(id=None, session_id="s1", role="admin",
                        message="Hola", timestamp=datetime.utcnow())

    def test_empty_message_raises_error(self):
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(id=None, session_id="s1", role="user",
                        message="", timestamp=datetime.utcnow())

    def test_whitespace_message_raises_error(self):
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(id=None, session_id="s1", role="user",
                        message="   ", timestamp=datetime.utcnow())

    def test_empty_session_id_raises_error(self):
        with pytest.raises(ValueError, match="sesion"):
            ChatMessage(id=None, session_id="", role="user",
                        message="Hola", timestamp=datetime.utcnow())

    def test_valid_user_message(self, user_message):
        assert user_message.role == "user"
        assert user_message.is_from_user() is True
        assert user_message.is_from_assistant() is False

    def test_valid_assistant_message(self, assistant_message):
        assert assistant_message.role == "assistant"
        assert assistant_message.is_from_assistant() is True
        assert assistant_message.is_from_user() is False


# ------------------------------------------------------------------ #
#  Tests de ChatContext                                                #
# ------------------------------------------------------------------ #

class TestChatContext:

    def test_format_for_prompt_empty(self):
        context = ChatContext(messages=[])
        assert context.format_for_prompt() == ""

    def test_format_for_prompt_structure(self, user_message, assistant_message):
        context = ChatContext(messages=[user_message, assistant_message])
        result = context.format_for_prompt()
        assert "Usuario: Hola, busco zapatillas" in result
        assert "Asistente: Hola, con gusto te ayudo" in result

    def test_format_for_prompt_order(self, user_message, assistant_message):
        """El mensaje del usuario debe aparecer antes que el del asistente"""
        context = ChatContext(messages=[user_message, assistant_message])
        result = context.format_for_prompt()
        assert result.index("Usuario:") < result.index("Asistente:")

    def test_get_recent_messages_respects_limit(self):
        """Con más de max_messages, solo retorna los últimos"""
        messages = [
            ChatMessage(id=i, session_id="s1", role="user",
                        message=f"Mensaje {i}", timestamp=datetime.utcnow())
            for i in range(1, 9)  # 8 mensajes
        ]
        context = ChatContext(messages=messages, max_messages=6)
        recent = context.get_recent_messages()
        assert len(recent) == 6
        assert recent[0].message == "Mensaje 3"  # Empieza desde el 3ro
        assert recent[-1].message == "Mensaje 8"  # Termina en el último