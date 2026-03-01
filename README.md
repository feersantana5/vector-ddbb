# Vector Database RAG System 🚀

Sistema RAG (Retrieval-Augmented Generation) multi-framework para búsqueda semántica y generación de respuestas sobre documentos del mercado laboral juvenil. Implementa **3 enfoques diferentes** (LangChain, LlamaIndex, y clientes directos) para comparar frameworks y patrones de arquitectura.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Endpoints API](#-endpoints-api)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías](#-tecnologías)

## ✨ Características

- **3 implementaciones RAG diferentes**: LangChain, LlamaIndex, y clientes directos de Google Gemini
- **Clasificación inteligente**: Sistema que categoriza preguntas antes de buscar
- **Búsqueda vectorial optimizada**: Qdrant con índice HNSW para máxima eficiencia
- **Filtrado por categorías**: Búsqueda solo en secciones relevantes del documento
- **API REST asíncrona**: FastAPI con operaciones async end-to-end
- **Embeddings de última generación**: Google Gemini Embedding Model (`gemini-embedding-001`)
- **Generación con LLM**: Gemini 2.5 Flash Lite para respuestas precisas

## 🏗️ Arquitectura

### Flujo General

```
Usuario → API FastAPI
    ↓
Clasificación de Pregunta (LLM analiza categoría)
    ↓
Generación de Embeddings (gemini-embedding-001)
    ↓
Búsqueda Vectorial Filtrada (Qdrant con filtro de categoría)
    ↓
Recuperación Top-K Documentos (similarity search)
    ↓
Augmentación de Prompt (inyección de contexto)
    ↓
Generación de Respuesta (Gemini 2.5 Flash Lite)
    ↓
Respuesta Estructurada (answer + metadata)
```

### Componentes Principales

#### 1. **Base de Datos Vectorial - Qdrant**
- Docker container en `localhost:6333`
- 3 colecciones independientes: `langchain_index`, `llamaindex_index`, `qdrantclient_index`
- Índice HNSW optimizado (m=16, ef_construct=100)
- Almacenamiento persistente en `./qdrant_data`

#### 2. **Sistema de Clasificación**
- Carga dinámicamente categorías desde `data/summaries.json`
- LLM clasifica pregunta en categoría apropiada
- Si no coincide → respuesta "fuera de alcance"
- Filtro aplicado a búsqueda vectorial para mayor precisión

#### 3. **Las 3 Implementaciones**

**🔗 LangChain** (`/langchain/*`)
- LCEL (LangChain Expression Language) para pipelines
- `RunnableBranch` para routing condicional
- Structured output con Pydantic models
- Búsqueda con `QdrantVectorStore.asimilarity_search()`

**🦙 LlamaIndex** (`/llama_index/*`)
- `RouterQueryEngine` con selección automática
- `PydanticSingleSelector` para elegir herramienta
- `QueryEngineTool` por categoría con filtros metadata
- Integración nativa con Qdrant

**⚡ Clientes Directos** (`/clients/*`)
- APIs nativas de Google Gemini
- Control total del flujo RAG
- `response_schema` para structured output
- Acceso directo a Qdrant client

## 📦 Requisitos Previos

- Python 3.12.11
- Docker y Docker Compose
- API Key de Google Gemini ([obtener aquí](https://aistudio.google.com/apikey))
- UV o pip para gestión de dependencias

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/feersantana5/vector-ddbb.git
cd vector-ddbb
```

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
GOOGLE_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENROUTER_API_KEY="....." # alternativa
```

### 3. Instalar dependencias

**Con UV (recomendado):**
```bash
uv sync
```

**Con pip:**
```bash
pip install -r requirements.txt
```

### 4. Levantar Qdrant

```bash
docker-compose up -d
```

Verificar que Qdrant está corriendo:
```bash
curl http://localhost:6333/collections
```

### 5. Cargar datos vectoriales

**Nota**: Debes ejecutar scripts de procesamiento y carga de datos (si están disponibles en `scripts/`):

```bash
python scripts/load_data.py  # Ajustar según tu script de carga
```

## 💻 Uso

### Iniciar el servidor

```bash
python src/main.py
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación interactiva

Accede a la documentación Swagger:
```
http://localhost:8000/docs
```

### Ejemplo de uso con curl

**Búsqueda vectorial simple:**
```bash
curl -X POST "http://localhost:8000/langchain/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es la tasa de desempleo juvenil?"}'
```

**Sistema RAG completo:**
```bash
curl -X POST "http://localhost:8000/langchain/rag" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son las principales barreras de acceso al empleo para jóvenes?"}'
```

### Ejemplo con Python

```python
import requests

# Endpoint RAG con LangChain
response = requests.post(
    "http://localhost:8000/langchain/rag",
    json={"question": "¿Qué programas de formación existen para jóvenes?"}
)

result = response.json()
print(f"Respuesta: {result['answer']}")
print(f"Fuente: {result['source']}")
print(f"Razón: {result['source_reason']}")
```

## 🔌 Endpoints API

### Root
- `GET /` - Mensaje de bienvenida

### LangChain
- `POST /langchain/search` - Búsqueda vectorial (sin RAG)
  - **Body**: `{"query": "texto a buscar"}`
  - **Response**: Lista de documentos con scores

- `POST /langchain/rag` - Sistema RAG completo
  - **Body**: `{"question": "pregunta del usuario"}`
  - **Response**: 
    ```json
    {
      "question": "...",
      "answer": "...",
      "source": "categoria_seleccionada",
      "source_reason": "..."
    }
    ```

### LlamaIndex
- `POST /llama_index/search` - Búsqueda vectorial
- `POST /llama_index/rag` - Sistema RAG con RouterQueryEngine

### Clientes Directos
- `POST /clients/search` - Búsqueda con cliente Qdrant nativo
- `POST /clients/rag` - RAG con APIs de Google Gemini

## 📁 Estructura del Proyecto

```
vector-ddbb/
├── src/
│   ├── api/
│   │   ├── router_langchain.py      # Endpoints LangChain
│   │   ├── router_llamaindex.py     # Endpoints LlamaIndex
│   │   ├── router_clients.py        # Endpoints clientes directos
│   │   └── schema.py                # Modelos Pydantic
│   ├── processes/
│   │   ├── langchain_chain/
│   │   │   ├── chain.py            # Pipeline LCEL
│   │   │   ├── prompts.py          # Plantillas de prompts
│   │   │   └── structures.py       # Modelos de datos
│   │   ├── llamaindex_query_engine/
│   │   │   └── query_engine.py     # RouterQueryEngine
│   │   ├── client_process/
│   │   │   └── process.py          # Lógica RAG manual
│   │   └── __init__.py             # Carga de summaries
│   ├── services/
│   │   ├── embeddings.py           # Modelos de embeddings
│   │   ├── llms.py                 # Configuración LLMs
│   │   └── vector_store.py         # Clientes Qdrant
│   ├── app.py                      # FastAPI app
│   └── main.py                     # Entry point
├── data/
│   ├── informe_mercado_de_trabajo_jovenes.pdf
│   ├── summaries.json              # Categorías y descripciones
│   └── optimized_chunks/           # Chunks procesados
├── qdrant_data/                    # Persistencia Qdrant
├── config.yaml                     # Configuración Qdrant
├── docker-compose.yaml
├── pyproject.toml
├── .env.example
└── README.md
```

## 🛠️ Tecnologías

### Frameworks & Librerías
- **FastAPI** - API REST asíncrona
- **LangChain** - Framework RAG con LCEL
- **LlamaIndex** - Data framework para LLMs
- **Qdrant** - Base de datos vectorial
- **Pydantic** - Validación de datos

### Modelos IA
- **Google Gemini 2.5 Flash Lite** - Generación de respuestas
- **Gemini Embedding 001** - Embeddings de texto (768 dims)

### Infraestructura
- **Docker** - Containerización de Qdrant
- **Uvicorn** - ASGI server
- **UV** - Gestor de dependencias rápido

## 📊 Métricas de Rendimiento

- **Latencia búsqueda vectorial**: ~50-100ms
- **Latencia generación respuesta**: ~1-2s
- **Dimensión embeddings**: 768
- **Top-K retrieval**: 4-5 documentos
- **Índice HNSW**: m=16, ef_construct=100