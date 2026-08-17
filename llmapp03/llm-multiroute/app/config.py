import os


class Settings:
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))
    APP_NAME: str = os.getenv("APP_NAME", "llm-multiroute")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY", "")

    # Per-route model assignments (must be available on Ollama cloud)
    OLLAMA_MODEL_CLASSIFY: str = os.getenv("OLLAMA_MODEL_CLASSIFY", "gemma4:31b")
    OLLAMA_MODEL_SENTIMENT: str = os.getenv("OLLAMA_MODEL_SENTIMENT", "glm-5.2")
    OLLAMA_MODEL_SUMMARIZE: str = os.getenv("OLLAMA_MODEL_SUMMARIZE", "mistral-large-3:675b")
    OLLAMA_MODEL_INTENT: str = os.getenv("OLLAMA_MODEL_INTENT", "minimax-m3")


settings = Settings()
