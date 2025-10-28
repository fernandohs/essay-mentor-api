import json
import requests
from typing import Optional
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import meta, analyze, guide

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An API for analyzing and guiding essay writing"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(analyze.router)
app.include_router(guide.router)

@app.post("/llm-test")
def test_llm(question: str = Body(..., embed=True), temperature: Optional[float] = Body(None, embed=True)):
    """
    Simple endpoint to test the connection with the configured LLM model.
    Sends the 'question' to the configured LLM model via Ollama and returns its JSON response.
    
    Args:
        question: The question to ask the LLM
        temperature: Optional temperature value. If not provided, uses the default from settings.
                    Suggested values from config:
                    - 0.1 (LLM_TEMP_FOCUSED) - Maximum precision
                    - 0.3 (LLM_TEMP_BALANCED) - Balanced precision
                    - 0.6 (LLM_TEMP_CREATIVE) - Balanced creativity
                    - 0.9 (LLM_TEMP_HIGHLY_CREATIVE) - High creativity
    """
    # Use provided temperature or fall back to default
    temp_value = temperature if temperature is not None else settings.LLM_TEMPERATURE
    
    url = f"{settings.OLLAMA_URL}/api/generate"
    payload = {
        "model": settings.LLM_MODEL,
        "prompt": f"Respond in clear JSON format to the following question:\n\n{question}\n\nExample: {{\"response\": \"text\"}}",
        "options": {
            "temperature": temp_value,
            "num_predict": settings.LLM_NUM_PREDICT
        }
    }

    try:
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        # Ollama responds in JSON chunks; extract the text from each chunk
        full_output = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk_data = json.loads(line.decode("utf-8"))
                    if "response" in chunk_data:
                        full_output += chunk_data["response"]
                except (json.JSONDecodeError, KeyError):
                    continue

        # Try to parse the output as JSON if possible
        cleaned_output = full_output.strip()
        parsed_output = cleaned_output
        
        try:
            # If the output is a valid JSON, parse it
            if cleaned_output.startswith('{') or cleaned_output.startswith('['):
                parsed_output = json.loads(cleaned_output)
        except (json.JSONDecodeError, ValueError):
            # If the output is not a valid JSON, leave it as text
            pass

        return {
            "model": settings.LLM_MODEL,
            "output": parsed_output
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {e}")