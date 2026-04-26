

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from src.domain.entities import Product
from src.domain.entities import ChatMessage
from src.application.product_service import ProductService, ProductNotFoundError
from src.application.chat_service import ChatService, ChatServiceError
from src.application.dtos import ProductDTO
from src.application.dtos import ChatMessageRequestDTO


# ------------------------------------------------------------------ #
#  Factories helpers                                                   #
# ------------------------------------------------------------------ #

def make_product(id=1, name="Air Max 270", brand="Nike",
                 category="Running", price=150.0, stock=10):
    return Product(
        id=id, name=name, brand=brand, category=category,
        size="42", color="Negro", price=price,
        stock=stock, description="Test",
    )


def make_product_dto(**kwargs):
    defaults = dict(
        id=None, name="Air Max 270", brand="Nike", category="Running",
        size="42", color="Negro", price=150.0, stock=10, description="Test",
    )
    defaults.update(kwargs)
    return ProductDTO(**defaults)


def make_chat_message(id=1, role="user", message="Hola", session_id="s1"):
    return ChatMessage(
        id=id, session_id=session_id, role=role,
        message=message, timestamp=datetime.utcnow(),
    )


# ------------------------------------------------------------------ #
#  Fixtures — mocks de repositorios                                   #
# ------------------------------------------------------------------ #

@pytest.fixture
def mock_product_repo():
    repo = MagicMock()
    repo.get_all.return_value = [
        make_product(id=1, name="Air Max 270", brand="Nike"),
        make_product(id=2, name="Ultraboost 22", brand="Adidas", stock=0),
    ]
    repo.get_by_id.return_value = make_product(id=1)
    repo.save.side_effect = lambda p: p  # Devuelve el mismo producto
    repo.delete.return_value = True
    return repo


@pytest.fixture
def mock_chat_repo():
    repo = MagicMock()
    repo.get_recent_messages.return_value = [
        make_chat_message(id=1, role="user", message="Busco zapatillas"),
        make_chat_message(id=2, role="assistant", message="Con gusto te ayudo"),
    ]
    repo.get_session_history.return_value = [
        make_chat_message(id=1, role="user", message="Busco zapatillas"),
    ]
    repo.save_message.side_effect = lambda m: m
    repo.delete_session_history.return_value = 3
    return repo


@pytest.fixture
def mock_gemini():
    gemini = MagicMock()
    gemini.generate_response = AsyncMock(
        return_value="Te recomiendo el Air Max 270 de Nike a $150."
    )
    return gemini


@pytest.fixture
def product_service(mock_product_repo):
    return ProductService(mock_product_repo)


@pytest.fixture
def chat_service(mock_product_repo, mock_chat_repo, mock_gemini):
    return ChatService(
        product_repository=mock_product_repo,
        chat_repository=mock_chat_repo,
        gemini_service=mock_gemini,
    )


# ------------------------------------------------------------------ #
#  Tests de ProductService                                             #
# ------------------------------------------------------------------ #

class TestProductServiceGetAll:

    def test_returns_all_products(self, product_service, mock_product_repo):
        result = product_service.get_all_products()
        assert len(result) == 2
        mock_product_repo.get_all.assert_called_once()

    def test_returns_dtos(self, product_service):
        result = product_service.get_all_products()
        assert all(isinstance(p, ProductDTO) for p in result)

    def test_empty_repository(self, product_service, mock_product_repo):
        mock_product_repo.get_all.return_value = []
        result = product_service.get_all_products()
        assert result == []


class TestProductServiceGetById:

    def test_returns_correct_product(self, product_service, mock_product_repo):
        result = product_service.get_product_by_id(1)
        assert result.id == 1
        assert result.name == "Air Max 270"
        mock_product_repo.get_by_id.assert_called_once_with(1)

    def test_raises_if_not_found(self, product_service, mock_product_repo):
        mock_product_repo.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError, match="1"):
            product_service.get_product_by_id(1)


class TestProductServiceCreate:

    def test_creates_product_successfully(self, product_service, mock_product_repo):
        dto = make_product_dto()
        mock_product_repo.save.return_value = make_product(id=99)
        result = product_service.create_product(dto)
        assert isinstance(result, ProductDTO)
        mock_product_repo.save.assert_called_once()

    def test_create_calls_save_with_no_id(self, product_service, mock_product_repo):
        dto = make_product_dto(id=None)
        mock_product_repo.save.return_value = make_product(id=1)
        product_service.create_product(dto)
        saved_entity = mock_product_repo.save.call_args[0][0]
        assert saved_entity.id is None

    def test_create_invalid_price_raises(self, product_service):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            make_product_dto(price=-10.0)

    def test_create_negative_stock_raises(self, product_service):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            make_product_dto(stock=-5)

class TestProductServiceUpdate:

    def test_updates_existing_product(self, product_service, mock_product_repo):
        dto = make_product_dto(price=200.0)
        mock_product_repo.save.return_value = make_product(id=1, price=200.0)
        result = product_service.update_product(1, dto)
        assert result.price == 200.0
        mock_product_repo.save.assert_called_once()

    def test_raises_if_product_not_found(self, product_service, mock_product_repo):
        mock_product_repo.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.update_product(99, make_product_dto())


class TestProductServiceDelete:

    def test_deletes_existing_product(self, product_service, mock_product_repo):
        result = product_service.delete_product(1)
        assert result is True
        mock_product_repo.delete.assert_called_once_with(1)

    def test_raises_if_product_not_found(self, product_service, mock_product_repo):
        mock_product_repo.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.delete_product(99)


class TestProductServiceAvailable:

    def test_returns_only_products_with_stock(self, product_service):
        """El fixture tiene 1 con stock=10 y 1 con stock=0"""
        result = product_service.get_available_products()
        assert len(result) == 1
        assert result[0].name == "Air Max 270"

    def test_empty_when_all_out_of_stock(self, product_service, mock_product_repo):
        mock_product_repo.get_all.return_value = [
            make_product(stock=0),
            make_product(id=2, stock=0),
        ]
        result = product_service.get_available_products()
        assert result == []


class TestProductServiceSearch:

    def test_filter_by_brand(self, product_service, mock_product_repo):
        mock_product_repo.get_all.return_value = [
            make_product(id=1, brand="Nike"),
            make_product(id=2, brand="Adidas"),
        ]
        result = product_service.search_products({"brand": "Nike"})
        assert len(result) == 1
        assert result[0].brand == "Nike"

    def test_filter_by_price_range(self, product_service, mock_product_repo):
        mock_product_repo.get_all.return_value = [
            make_product(id=1, price=80.0),
            make_product(id=2, price=150.0),
            make_product(id=3, price=200.0),
        ]
        result = product_service.search_products({"min_price": 100.0, "max_price": 160.0})
        assert len(result) == 1
        assert result[0].price == 150.0

    def test_empty_filters_returns_all(self, product_service):
        result = product_service.search_products({})
        assert len(result) == 2


# ------------------------------------------------------------------ #
#  Tests de ChatService                                                #
# ------------------------------------------------------------------ #

class TestChatServiceProcessMessage:

    @pytest.mark.asyncio
    async def test_returns_response_dto(self, chat_service):
        request = ChatMessageRequestDTO(
            session_id="s1", message="Busco zapatillas Nike"
        )
        result = await chat_service.process_message(request)
        assert result.session_id == "s1"
        assert result.user_message == "Busco zapatillas Nike"
        assert "Air Max" in result.assistant_message

    @pytest.mark.asyncio
    async def test_saves_both_messages(self, chat_service, mock_chat_repo):
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)
        assert mock_chat_repo.save_message.call_count == 2

    @pytest.mark.asyncio
    async def test_saves_user_message_first(self, chat_service, mock_chat_repo):
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)
        first_call = mock_chat_repo.save_message.call_args_list[0][0][0]
        assert first_call.role == "user"
        assert first_call.message == "Hola"

    @pytest.mark.asyncio
    async def test_saves_assistant_message_second(self, chat_service, mock_chat_repo):
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)
        second_call = mock_chat_repo.save_message.call_args_list[1][0][0]
        assert second_call.role == "assistant"

    @pytest.mark.asyncio
    async def test_gemini_error_raises_chat_service_error(
        self, chat_service, mock_gemini
    ):
        mock_gemini.generate_response = AsyncMock(
            side_effect=Exception("API timeout")
        )
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        with pytest.raises(ChatServiceError, match="API timeout"):
            await chat_service.process_message(request)

    @pytest.mark.asyncio
    async def test_uses_recent_messages_for_context(
        self, chat_service, mock_chat_repo
    ):
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)
        mock_chat_repo.get_recent_messages.assert_called_once_with("s1", count=6)


class TestChatServiceHistory:

    def test_get_session_history(self, chat_service, mock_chat_repo):
        result = chat_service.get_session_history("s1", limit=10)
        assert len(result) == 1
        mock_chat_repo.get_session_history.assert_called_once_with("s1", limit=10)

    def test_clear_session_history(self, chat_service, mock_chat_repo):
        result = chat_service.clear_session_history("s1")
        assert result == 3
        mock_chat_repo.delete_session_history.assert_called_once_with("s1")