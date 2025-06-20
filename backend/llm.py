from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from langchain_ollama import ChatOllama
import os

load_dotenv()
AI_PLATFORM = os.getenv("AI_PLATFORM")
WATSONX_MODEL_ID = os.getenv("WATSONX_MODEL_ID")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
OLLAMA_MODEL_ID = os.getenv("OLLAMA_MODEL_ID_ALT_1")

def get_llm():

    if "watsonx" in AI_PLATFORM:
        kwargs = {
            "project_id": WATSONX_PROJECT_ID,
            "credentials": Credentials(
                url = WATSONX_URL,
                api_key = WATSONX_APIKEY
            ),
            "params": {
                "temperature": 0
            }
        }
        llm = init_chat_model(model=WATSONX_MODEL_ID, model_provider="ibm", **kwargs)  
        print(f"Model in use: {llm.model_id}") 
        return llm
    
    else:
        # Ollama LLM
        llm = ChatOllama(model=OLLAMA_MODEL_ID, base_url="http://localhost:11434")
        print(f"Model in use: {llm.model}") 
        return llm