from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data():
    """
    Carga productos de ejemplo si la tabla está vacía.
    Se llama una sola vez al arrancar la aplicación.
    """
    db = SessionLocal()
    try:
        # Si ya hay productos no hace nada
        if db.query(ProductModel).count() > 0:
            print("✓ Productos ya existentes, omitiendo carga inicial.")
            return

        products = [
            ProductModel(
                name="Air Max 270",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro/Blanco",
                price=150.00,
                stock=25,
                description="Zapatilla de running con amortiguación Air Max para máximo confort.",
            ),
            ProductModel(
                name="Ultraboost 22",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=180.00,
                stock=15,
                description="Zapatilla de alto rendimiento con tecnología Boost para corredores.",
            ),
            ProductModel(
                name="RS-X Toys",
                brand="Puma",
                category="Casual",
                size="43",
                color="Multicolor",
                price=110.00,
                stock=30,
                description="Zapatilla retro con diseño llamativo, ideal para uso diario.",
            ),
            ProductModel(
                name="Chuck Taylor All Star",
                brand="Converse",
                category="Casual",
                size="40",
                color="Rojo",
                price=75.00,
                stock=40,
                description="Clásico atemporal de lona, perfecto para looks casuales.",
            ),
            ProductModel(
                name="Old Skool",
                brand="Vans",
                category="Casual",
                size="42",
                color="Negro/Blanco",
                price=85.00,
                stock=35,
                description="Icónica zapatilla de skate con la clásica franja lateral.",
            ),
            ProductModel(
                name="Gel-Kayano 29",
                brand="Asics",
                category="Running",
                size="44",
                color="Azul/Naranja",
                price=160.00,
                stock=20,
                description="Zapatilla de running con soporte superior para largas distancias.",
            ),
            ProductModel(
                name="Fresh Foam 1080",
                brand="New Balance",
                category="Running",
                size="41",
                color="Gris",
                price=170.00,
                stock=18,
                description="Amortiguación premium Fresh Foam para entrenamientos intensos.",
            ),
            ProductModel(
                name="Classic Leather",
                brand="Reebok",
                category="Formal",
                size="43",
                color="Blanco",
                price=95.00,
                stock=22,
                description="Zapatilla de cuero con diseño minimalista, apta para ocasiones formales.",
            ),
            ProductModel(
                name="Suede Classic",
                brand="Puma",
                category="Formal",
                size="42",
                color="Azul Marino",
                price=90.00,
                stock=0,
                description="Zapatilla de gamuza elegante, un clásico para looks formales.",
            ),
            ProductModel(
                name="Court Vision Low",
                brand="Nike",
                category="Casual",
                size="40",
                color="Blanco/Gris",
                price=80.00,
                stock=50,
                description="Zapatilla inspirada en el basketball con estilo limpio y versátil.",
            ),
        ]

        db.add_all(products)
        db.commit()
        print(f"✓ {len(products)} productos cargados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"✗ Error al cargar datos iniciales: {e}")
        raise
    finally:
        db.close()