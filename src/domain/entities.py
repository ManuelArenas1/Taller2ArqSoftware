from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# Creamos la entidad de Producto
@dataclass
class Product:
    """ 
    Entidad que representa un producto en el e-commerce.
    Contiene la logica de negocio relacionada con los productos.
    """
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self):
        """
        Validaciones que se ejecutan despues de crear el objeto.
        TODO: Implementar validaciones.
        - price debe ser mayor a 0.
        - stock no puede ser negativo
        - name no puede estar vacio
        Lanza ValueError si alguna validacion falla.
        """
         # implementa aqui las validaciones
        if self.price <= 0:
            raise ValueError("El precio no puede ser menor que 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        if not self.name or self.name.strip() == "":
            raise ValueError("El nombre no puede estar vacio")
        

    def is_available(self) -> bool:
        """
        TODO: Retorna True si el producto tiene stock disponible
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        TODO: Reduce el stock del producto
        - valida que el quantity sea positivo
        - valida que haya suficiente stock
        - lanza ValueError si no se puede reducir
        """
        if quantity <= 0:
            raise ValueError("La cantidad tiene que ser positiva para poderse reducir")
        
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock disponible")
        
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        TODO: Aumenta el stock del producto
        - Valida que quantity sea positivo
        """
        if quantity <= 0: 
            raise ValueError("La cantidad a aumentar tiene que ser positiva")
        
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en el chat.
    """
    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime
    
    def __post_init__(self):
        """
        TODO: Implementar validaciones:
        - role debe ser 'user' o 'assistant'
        - message no puede estar vacío
        - session_id no puede estar vacío
        """
        if self.role not in['user','assistant']:
            raise ValueError("El rol tiene que ser 'user' o 'assistant'.")
        
        if not self.message or self.message.strip() == "":
            raise ValueError("El mensaje no puede estar vacio")
        
        if not self.session_id or self.session_id.strip() == "":
            raise ValueError("El id de sesion no puede estar vacio")
        
    
    def is_from_user(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del usuario
        """
        return self.role == 'user'
    
    def is_from_assistant(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del asistente
        """
        return self.role == 'assistant'

@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.
    Mantiene los mensajes recientes para dar coherencia al chat.
    """
    messages: list[ChatMessage]
    max_messages: int = 6
    
    def get_recent_messages(self) -> list[ChatMessage]:
        """
        TODO: Retorna los últimos N mensajes (max_messages)
        Pista: Usa slicing de Python messages[-self.max_messages:]
        """
        return self.messages[-self.max_messages:]
    
    def format_for_prompt(self) -> str:
        """
        TODO: Formatea los mensajes para incluirlos en el prompt de IA
        Formato esperado:
        "Usuario: mensaje del usuario
        Asistente: respuesta del asistente
        Usuario: otro mensaje
        ..."
        
        Pista: Itera sobre get_recent_messages() y construye el string
        """
        formatted_messages = []

        for msg in self.get_recent_messages():
            if msg.is_from_user():
                prefix = "Usuario"
            else:
                prefix = "Asistente"
            
            formatted_messages.append(f"{prefix}: {msg.message}")
        
        return "\n".join(formatted_messages)

    