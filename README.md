# E-commerce Chat IA

API REST que expone un catálogo de zapatos y un chat conversacional potenciado por Google Gemini, siguiendo principios de Clean Architecture. El proyecto fue desarrollado como parte del taller "Construcción de E-commerce con Chat IA" de la Universidad EAFIT.

## Características
- Gestión completa del catálogo de productos (listar, filtrar, CRUD).
- Chat inteligente que combina contexto conversacional con el inventario disponible.
- Arquitectura en capas (Dominio, Aplicación e Infraestructura) desacoplada de frameworks.
- Persistencia con SQLite mediante SQLAlchemy.
- Integración con Gemini a través de `google-generativeai`.
- Contenedorización con Docker y soporte para ejecución local.
- Suite de pruebas unitarias con Pytest.

## Arquitectura
```
┌──────────────────────────────────────────┐
│             Cliente (HTTP)               │
└──────────────────────┬───────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────┐
│        Infraestructura (FastAPI)         │
│  - Endpoints REST                        │
│  - Repositorios SQLAlchemy               │
│  - Servicio Gemini                       │
└──────────────────────┬───────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────┐
│          Aplicación (Servicios)          │
│  - ProductService                        │
│  - ChatService                           │
│  - DTOs con Pydantic                     │
└──────────────────────┬───────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────┐
│            Dominio (Entidades)           │
│  - Product, ChatMessage, ChatContext     │
│  - Repositorios abstractos               │
│  - Excepciones del dominio               │
└──────────────────────────────────────────┘
```

## Requisitos Previos
- Python 3.11 o superior.
- Cuenta en Google AI Studio con API Key de Gemini.
- (Opcional) Docker Desktop para ejecución en contenedor.

## Estructura del Proyecto
```
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── tests/
└── data/
```

## Configuración Local
1. Clona el repositorio y entra al directorio del proyecto.
2. Crea y activa un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Crea el archivo `.env` (puedes partir de `.env.example`):
   ```env
   GEMINI_API_KEY=TU_API_KEY
   DATABASE_URL=sqlite:///./data/ecommerce_chat.db
   ENVIRONMENT=development
   ```
5. Ejecuta la API:
   ```bash
   uvicorn src.infrastructure.api.main:app --reload
   ```
6. Ingresa a `http://127.0.0.1:8000/docs` para explorar Swagger.

## Ejecución con Docker
1. Asegúrate de tener Docker Desktop en ejecución.
2. Construye y levanta el servicio:
   ```bash
   docker compose up --build
   ```
3. Accede a `http://localhost:8000/docs`.
4. Para detener el contenedor:
   ```bash
   docker compose down
   ```

## Variables de Entorno Importantes
| Variable | Descripción |
|----------|-------------|
| `GEMINI_API_KEY` | API Key obtenida en Google AI Studio. |
| `DATABASE_URL` | Cadena de conexión a SQLite. En Docker se usa `sqlite:////app/data/ecommerce_chat.db`. |
| `ENVIRONMENT` | Entorno de ejecución (`development`, `production`, etc.). |

## Endpoints Destacados
- `GET /products`: Lista productos del catálogo.
- `GET /products/{product_id}`: Obtiene un producto por ID.
- `POST /chat`: Procesa un mensaje y retorna la respuesta de la IA.
- `GET /chat/history/{session_id}`: Historial conversacional por sesión.
- `DELETE /chat/history/{session_id}`: Elimina el historial.
- `GET /health`: Health check básico.

### Ejemplo de `POST /chat`
```http
POST /chat
Content-Type: application/json

{
  "session_id": "demo",
  "message": "Busco zapatos para correr talla 42"
}
```
Respuesta:
```json
{
  "session_id": "demo",
  "user_message": "Busco zapatos para correr talla 42",
  "assistant_message": "Respuesta generada por Gemini...",
  "timestamp": "2025-11-06T15:30:00"
}
```

## Pruebas
Ejecuta la suite de tests con:
```bash
source venv/bin/activate
pytest
```
Los tests cubren validaciones de entidades y los casos de uso de ProductService y ChatService mediante repositorios en memoria.

## Evidencias Requeridas
Se capturaron las evidencias solicitadas en el taller y se almacenarán en `evidencias/`:
1. Swagger UI de la API.
2. Docker corriendo la aplicación.
3. Logs de Docker mostrando actividad.
4. Petición `GET /products` desde Postman.
5. Petición `POST /chat` desde Postman con respuesta de la IA.
6. Visualización de la base de datos SQLite con los productos iniciales.

## Tecnologías
- FastAPI
- SQLAlchemy
- Pydantic
- Google Gemini (`google-generativeai`)
- Docker / Docker Compose
- Pytest

## Checklist Final
- [x] Arquitectura en capas implementada.
- [x] Integración con Gemini.
- [x] Persistencia y datos semilla en SQLite.
- [x] Dockerfile y docker-compose listos.
- [x] Pruebas unitarias en `tests/`.
- [x] Documentación (README y evidencias).

---
Si necesitas ejecutar el proyecto en otro entorno o desplegarlo, asegúrate de replicar las variables de entorno y ajustar la URL de la base de datos según corresponda.