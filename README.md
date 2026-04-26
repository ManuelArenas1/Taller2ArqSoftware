# 🛍️ E-Commerce Chat AI
 
API REST para un e-commerce de zapatos con asistente de inteligencia artificial integrado. Permite gestionar productos y chatear con una IA que recomienda productos basándose en el catálogo disponible.
 
---
 
## 🏗️ Arquitectura
 
El proyecto sigue los principios de **Arquitectura Limpia (Clean Architecture)**:
 
```
src/
├── domain/                     # Entidades y contratos del negocio
│   ├── entities/
│   │   ├── product.py          # Entidad Product
│   │   └── chat_message.py     # Entidad ChatMessage / ChatContext
│   └── repositories/
│       ├── product_repository.py
│       └── chat_repository.py
├── application/                # Casos de uso y servicios
│   ├── product_service.py
│   ├── chat_service.py
│   └── dtos/
│       ├── product_dto.py
│       └── chat_dto.py
└── infrastructure/             # Implementaciones concretas
    ├── api/
│   └── main.py             # FastAPI app y endpoints
    ├── db/
    │   ├── database.py         # Configuración SQLAlchemy
    │   ├── models.py           # Modelos ORM
    │   └── init_data.py        # Datos iniciales
    ├── repositories/
    │   ├── product_repository.py
    │   └── chat_repository.py
    └── llm_providers/
        └── gemini_services.py   # Integración con Google Gemini
```
 
---
 
## ⚙️ Requisitos
 
- Python 3.11+
- Docker y Docker Compose
- API Key de Google Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))
---
 
## 🚀 Instalación y uso
 
### Con Docker (recomendado)
 
**1. Clona el repositorio**
 
```bash
git clone https://github.com/ManuelArenas1/Taller2ArqSoftware.git
cd Taller2ArqSoftware
```
 
**2. Crea el archivo `.env`**
 
```bash
cp .env.example .env
```
 
Edita `.env` y agrega tu API key:
 
```env
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
```
 
**3. Construye y levanta los contenedores**
 
```bash
docker-compose up --build
```
 
La API estará disponible en `http://localhost:8000`.
 
---
 
### Sin Docker (entorno local)
 
**1. Crea y activa el entorno virtual**
 
```bash
python -m venv venv
 
# Windows
venv\Scripts\activate
 
# Linux / Mac
source venv/bin/activate
```
 
**2. Instala las dependencias**
 
```bash
pip install -r requirements.txt
```
 
**3. Crea el archivo `.env`**
 
```env
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
```
 
**4. Crea la carpeta de datos**
 
```bash
mkdir data
```
 
**5. Levanta la aplicación**
 
```bash
uvicorn src.infrastructure.api.main:app --reload
```
 
---
 
## 📡 Endpoints
 
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Health check |
| `GET` | `/products` | Lista todos los productos |
| `GET` | `/products/{id}` | Obtiene producto por ID |
| `POST` | `/chat` | Envía mensaje al asistente IA |
| `GET` | `/chat/history/{session_id}` | Historial de una sesión |
| `DELETE` | `/chat/history/{session_id}` | Elimina historial de sesión |
 
Documentación interactiva disponible en `http://localhost:8000/docs`.
 
---
 
## 💬 Uso del Chat
 
**Request:**
 
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sesion-001",
    "message": "Busco zapatillas Nike para correr"
  }'
```
 
**Response:**
 
```json
{
  "session_id": "sesion-001",
  "user_message": "Busco zapatillas Nike para correr",
  "assistant_message": "¡Hola! Te recomiendo el Air Max 270 de Nike a $150.00...",
  "timestamp": "2026-04-26T10:30:00"
}
```
 
---
 
## 🧪 Tests
 
```bash
# Instala dependencias de testing
pip install pytest pytest-asyncio pytest-cov
 
# Ejecutar todos los tests
pytest tests/ -v
 
# Ejecutar con cobertura
pytest tests/ --cov=src --cov-report=term-missing
 
# Verificar cobertura mínima del 80%
pytest tests/ --cov=src --cov-fail-under=80
```
 
---
 
## 🗄️ Base de Datos
 
El proyecto usa **SQLite** con SQLAlchemy. La base de datos se crea automáticamente al iniciar la aplicación y se carga con 10 productos de ejemplo.
 
Para visualizar la base de datos puedes usar:
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- Extensión **SQLite Viewer** en VS Code
Archivo de base de datos: `data/ecommerce_chat.db`
 
---
 
## 🐳 Comandos Docker útiles
 
```bash
# Levantar en background
docker-compose up -d --build
 
# Ver logs en tiempo real
docker-compose logs -f
 
# Reconstruir sin caché
docker-compose build --no-cache
docker-compose up
 
# Detener contenedores
docker-compose down
 
# Detener y eliminar volúmenes
docker-compose down -v
```
 
---
 
## 📦 Tecnologías
 
| Tecnología | Uso |
|------------|-----|
| FastAPI | Framework web y API REST |
| SQLAlchemy | ORM y acceso a base de datos |
| SQLite | Base de datos |
| Pydantic | Validación de datos y DTOs |
| Google Gemini | Modelo de IA para el chat |
| Docker | Containerización |
| Pytest | Testing unitario |
 
---
 
## 🔒 Variables de entorno
 
| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GEMINI_API_KEY` | API Key de Google Gemini | ✅ Sí |
| `DATABASE_URL` | URL de conexión a la BD | ❌ Tiene default |
 
> ⚠️ **Nunca subas tu `.env` a Git.** Está incluido en `.gitignore`.
