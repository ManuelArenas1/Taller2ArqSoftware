from typing import List, Optional, Dict, Any
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.application.dtos import ProductDTO


class ProductNotFoundError(Exception):
    """Se lanza cuando un producto no existe en el repositorio"""
    pass


class ProductService:
    """
    Servicio de aplicación para gestión de productos.
    Orquesta la lógica entre los DTOs, entidades y el repositorio.
    """

    def __init__(self, repository: IProductRepository):
        self._repository = repository

    # ------------------------------------------------------------------ #
    #  Helpers   hechos para no repetir codigo                           #
    # ------------------------------------------------------------------ #

    def _dto_to_entity(self, dto: ProductDTO, product_id: Optional[int] = None) -> Product:
        """Convierte un ProductDTO a una entidad Product"""
        return Product(
            id=product_id if product_id is not None else dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description,
        )

    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """Convierte una entidad Product a ProductDTO"""
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )

    def _get_or_raise(self, product_id: int) -> Product:
        """Busca el producto o lanza ProductNotFoundError"""
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Producto con ID {product_id} no encontrado")
        return product

    # ------------------------------------------------------------------ #
    #  Métodos públicos                                                    #
    # ------------------------------------------------------------------ #

    def get_all_products(self) -> List[ProductDTO]:
        """Retorna todos los productos"""
        products = self._repository.get_all()
        return [self._entity_to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """Busca un producto por ID, lanza excepción si no existe"""
        product = self._get_or_raise(product_id)
        return self._entity_to_dto(product)

    def search_products(self, filters: Dict[str, Any]) -> List[ProductDTO]:
        """
        Filtra productos según los criterios recibidos.
        Filtros soportados: brand, category, min_price, max_price
        """
        # Punto de partida: todos los productos
        products = self._repository.get_all()

        brand = filters.get("brand")
        category = filters.get("category")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")

        if brand:
            products = [p for p in products if p.brand.lower() == brand.lower()]

        if category:
            products = [p for p in products if p.category.lower() == category.lower()]

        if min_price is not None:
            products = [p for p in products if p.price >= min_price]

        if max_price is not None:
            products = [p for p in products if p.price <= max_price]

        return [self._entity_to_dto(p) for p in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """Crea un nuevo producto a partir de un DTO"""
        # La entidad valida sus propias reglas en __post_init__
        product = self._dto_to_entity(product_dto, product_id=None)
        saved = self._repository.save(product)
        return self._entity_to_dto(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """Actualiza un producto existente"""
        self._get_or_raise(product_id)           # Valida que exista
        product = self._dto_to_entity(product_dto, product_id=product_id)
        updated = self._repository.save(product)
        return self._entity_to_dto(updated)

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto, lanza excepción si no existe"""
        self._get_or_raise(product_id)           # Valida que exista
        return self._repository.delete(product_id)

    def get_available_products(self) -> List[ProductDTO]:
        """Retorna solo los productos con stock disponible"""
        products = self._repository.get_all()
        available = [p for p in products if p.is_available()]
        return [self._entity_to_dto(p) for p in available]