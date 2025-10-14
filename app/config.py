import os
from dotenv import load_dotenv

load_dotenv()

# API Keys & Paths
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CODEBASE_PATH = os.getenv("CODEBASE_PATH")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")

# Models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
LLM_MODEL = os.getenv("LLM_MODEL")

# LLM parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.1))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048))
