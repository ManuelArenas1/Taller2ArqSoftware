
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementación concreta del repositorio de productos con SQLAlchemy.
    La capa de dominio nunca ve modelos ORM, solo entidades Product.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Helpers de conversión                                               #
    # ------------------------------------------------------------------ #

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convierte un modelo ORM a entidad de dominio"""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad de dominio a modelo ORM"""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )

    # ------------------------------------------------------------------ #
    #  Métodos del contrato                                                #
    # ------------------------------------------------------------------ #

    def get_all(self) -> List[Product]:
        """Retorna todos los productos"""
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Retorna un producto por ID o None si no existe"""
        model = (
            self.db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """Retorna productos de una marca (búsqueda insensible a mayúsculas)"""
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.brand.ilike(brand))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """Retorna productos de una categoría (búsqueda insensible a mayúsculas)"""
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.category.ilike(category))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        """
        Crea o actualiza según si el producto tiene ID.
        Retorna la entidad con el ID asignado por la BD.
        """
        if product.id is None:
            # --- Crear nuevo ---
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)   # Obtiene el ID generado por autoincrement
        else:
            # --- Actualizar existente ---
            model = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product.id)
                .first()
            )
            if model is None:
                raise ValueError(f"Producto con ID {product.id} no encontrado")

            model.name = product.name
            model.brand = product.brand
            model.category = product.category
            model.size = product.size
            model.color = product.color
            model.price = product.price
            model.stock = product.stock
            model.description = product.description
            self.db.commit()
            self.db.refresh(model)

        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID. Retorna True si existía, False si no."""
        model = (
            self.db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True