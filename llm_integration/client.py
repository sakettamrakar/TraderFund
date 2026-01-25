import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Try to import llama_cpp, handle if not installed
try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

load_dotenv()
logger = logging.getLogger("LLMClient")

class LocalLLMClient:
    """
    Wrapper for local LLM execution using llama-cpp-python.
    """
    _instance = None

    def __init__(self, model_path: str):
        if not HAS_LLAMA_CPP:
            raise ImportError("llama-cpp-python is required for LocalLLMClient")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
            
        logger.info(f"Loading local LLM from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,      # Standard context window
            n_threads=4,     # Parallel threads
            verbose=False    # Suppress llama.cpp internal logs
        )
        logger.info("Local LLM loaded successfully.")

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
        """
        Generates text using the loaded model.
        """
        prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
        
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            stop=["User:", "System:", "\n\n"],
            echo=False
        )
        
        return output['choices'][0]['text'].strip()

def get_llm_client() -> Optional[LocalLLMClient]:
    """
    Singleton factory for the LLM client.
    """
    if LocalLLMClient._instance is None:
        model_path = os.getenv("LLM_MODEL_PATH")
        if not model_path:
            logger.warning("LLM_MODEL_PATH not set in environment. Falling back to Mock.")
            return None
            
        try:
            LocalLLMClient._instance = LocalLLMClient(model_path)
        except Exception as e:
            logger.error(f"Failed to initialize Local LLM: {e}")
            return None
            
    return LocalLLMClient._instance
