# Project Structure

  llm-python/
  ├── requirements.txt              # FastAPI, uvicorn, httpx, pydantic,
  pytest
  ├── app/
  │   ├── __init__.py
  │   ├── main.py                   # FastAPI app entry point (Swagger at
  /swagger-ui.html)
  │   ├── config.py                 # Settings (Ollama URL, model,
  temperature)
  │   ├── controller/
  │   │   ├── __init__.py
  │   │   └── ai_controller.py     # 4 REST endpoints under /api/ai/
  │   ├── service/
  │   │   ├── __init__.py
  │   │   └── ai_service.py        # Ollama chat integration + JSON parsing 
  │   └── dto/
  │       ├── __init__.py
  │       ├── text_request.py       # Pydantic request model
  │       ├── classification_response.py
  │       ├── sentiment_response.py
  │       ├── summary_response.py
  │       └── intent_response.py tests/
      ├── __init__.py 
      ├── test_ai_controller.py     # 19 endpoint tests
      └── test_ai_service.py        # 22 service/parsing tests

  # Mapping Summary
  ┌───────────────────────────────┬─────────────────────────────────────┐
  │          Spring Boot          │          Python (FastAPI)           │
  ├───────────────────────────────┼─────────────────────────────────────┤  
  │ Spring Boot Web               │ FastAPI + Uvicorn                   │
  ├───────────────────────────────┼─────────────────────────────────────┤  
  │ Spring AI ChatClient (Ollama) │ httpx (direct Ollama REST API)      │
  ├───────────────────────────────┼─────────────────────────────────────┤
  │ Java DTOs with Jackson        │ Pydantic models                     │
  ├───────────────────────────────┼─────────────────────────────────────┤
  │ SpringDoc OpenAPI / Swagger   │ FastAPI built-in OpenAPI            │
  ├───────────────────────────────┼─────────────────────────────────────┤
  │ JUnit 5 + Mockito             │ pytest + unittest.mock              │
  ├───────────────────────────────┼─────────────────────────────────────┤
  │ application.yml               │ Environment variables via config.py │
  └───────────────────────────────┴─────────────────────────────────────┘
  
  # Endpoints (identical to Spring Boot)
  - POST /api/ai/classify - Text classification
  - POST /api/ai/sentiment - Sentiment analysis
  - POST /api/ai/summarize - Text summarization
  - POST /api/ai/intent - Intent detection
  
  # Running
  cd llm-python
  pip install -r requirements.txt
  python -m uvicorn app.main:app --port 8080 --reload

  Swagger UI is at http://localhost:8080/swagger-ui.html (same Ollama
  requirement: http://localhost:11434 with gemma:2b).