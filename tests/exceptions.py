"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""

class ProductNotFoundError(Exception):
    """
    Se lanza cuando se busca un producto que no existe.
    
    TODO: Implementa el constructor:
    - Debe aceptar un product_id opcional
    - Mensaje por defecto: "Producto no encontrado"
    - Si se pasa product_id: "Producto con ID {product_id} no encontrado"
    """
    def __init__(self, product_id: int = None):
        if product_id is not None:
            message = f"Producto con ID {product_id} no encontrado"
        else:
            message = "Producto no encontrado"
        
        super().__init__(message)


class InvalidProductDataError(Exception):
    """
    Se lanza cuando los datos de un producto son inválidos.
    
    TODO: Implementa el constructor:
    - Debe aceptar un mensaje personalizado
    - Mensaje por defecto: "Datos de producto inválidos"
    """
    def __init__(self, message: str = "Datos de producto inválidos"):
        super().__init__(message)


class ChatServiceError(Exception):
    """
    Se lanza cuando hay un error en el servicio de chat.
    
    TODO: Implementa el constructor:
    - Debe aceptar un mensaje personalizado
    - Mensaje por defecto: "Error en el servicio de chat"
    """
    def __init__(self, message: str = "Error en el servicio de chat"):
        super().__init__(message)
