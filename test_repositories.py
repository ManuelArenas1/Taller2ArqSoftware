# test_repositories.py  (en la raíz del proyecto)

from src.infrastructure.db.database import init_db, SessionLocal
from src.infrastructure.db.init_data import load_initial_data
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.domain.entities import Product
from src.domain.entities import ChatMessage
from datetime import datetime


def separador(titulo: str):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print('='*50)


def test_products(db):
    repo = SQLProductRepository(db)

    separador("GET ALL")
    products = repo.get_all()
    print(f"Total productos: {len(products)}")
    for p in products:
        print(f"  [{p.id}] {p.name} - {p.brand} - ${p.price}")

    separador("GET BY ID")
    product = repo.get_by_id(1)
    print(f"Producto ID 1: {product.name}")
    not_found = repo.get_by_id(9999)
    print(f"Producto ID 9999: {not_found}")  # Debe ser None

    separador("GET BY BRAND")
    nikes = repo.get_by_brand("Nike")
    print(f"Productos Nike: {len(nikes)}")
    for p in nikes:
        print(f"  {p.name}")

    separador("GET BY CATEGORY")
    running = repo.get_by_category("Running")
    print(f"Productos Running: {len(running)}")

    separador("CREATE")
    nuevo = Product(
        id=None,
        name="Test Shoe",
        brand="TestBrand",
        category="Casual",
        size="42",
        color="Verde",
        price=99.99,
        stock=10,
        description="Producto de prueba",
    )
    creado = repo.save(nuevo)
    print(f"Creado con ID: {creado.id} - {creado.name}")

    separador("UPDATE")
    creado.price = 149.99
    creado.stock = 20
    actualizado = repo.save(creado)
    print(f"Precio actualizado: ${actualizado.price} | Stock: {actualizado.stock}")

    separador("DELETE")
    resultado = repo.delete(actualizado.id)
    print(f"Eliminado: {resultado}")  # True
    resultado2 = repo.delete(9999)
    print(f"Eliminar inexistente: {resultado2}")  # False


def test_chat(db):
    repo = SQLChatRepository(db)
    session_id = "test-session-001"

    separador("SAVE MESSAGES")
    for i in range(1, 5):
        role = "user" if i % 2 != 0 else "assistant"
        msg = ChatMessage(
            id=None,
            session_id=session_id,
            role=role,
            message=f"Mensaje de prueba número {i}",
            timestamp=datetime.utcnow(),
        )
        guardado = repo.save_message(msg)
        print(f"Guardado ID {guardado.id} | {guardado.role}: {guardado.message}")

    separador("GET SESSION HISTORY (completo)")
    history = repo.get_session_history(session_id)
    print(f"Total mensajes: {len(history)}")
    for m in history:
        print(f"  [{m.id}] {m.role}: {m.message}")

    separador("GET SESSION HISTORY (limit=2)")
    limited = repo.get_session_history(session_id, limit=2)
    print(f"Últimos 2 mensajes:")
    for m in limited:
        print(f"  [{m.id}] {m.role}: {m.message}")

    separador("GET RECENT MESSAGES (3)")
    recent = repo.get_recent_messages(session_id, count=3)
    print(f"Últimos 3 mensajes en orden cronológico:")
    for m in recent:
        print(f"  [{m.id}] {m.role}: {m.message}")

    separador("DELETE SESSION HISTORY")
    eliminados = repo.delete_session_history(session_id)
    print(f"Mensajes eliminados: {eliminados}")
    history_post = repo.get_session_history(session_id)
    print(f"Mensajes tras eliminar: {len(history_post)}")  # 0


if __name__ == "__main__":
    print("Inicializando BD...")
    init_db()
    load_initial_data()

    db = SessionLocal()
    try:
        test_products(db)
        test_chat(db)
        print("\n✓ Todos los tests pasaron correctamente.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    finally:
        db.close()