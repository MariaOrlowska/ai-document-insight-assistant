import os

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    # dotenv not available or .env not found — continue using existing environment variables
    pass

# Document Intelligence / Form Recognizer config
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# Azure OpenAI config
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# Add API version (standard for Azure OpenAI)
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

# Compatibility: some Azure OpenAI libs expect AZURE_OPENAI_API_KEY env var name
if AZURE_OPENAI_KEY and not os.getenv("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_KEY

# Basic sanity checks to fail early with a clear message
_missing = []
if not AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
    _missing.append("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
if not AZURE_DOCUMENT_INTELLIGENCE_KEY:
    _missing.append("AZURE_DOCUMENT_INTELLIGENCE_KEY")
if not AZURE_OPENAI_KEY and not os.getenv("AZURE_OPENAI_API_KEY"):
    _missing.append("AZURE_OPENAI_KEY or AZURE_OPENAI_API_KEY")
if not AZURE_OPENAI_DEPLOYMENT:
    _missing.append("AZURE_OPENAI_DEPLOYMENT")

if _missing:
    raise RuntimeError("Missing environment variables: " + ", ".join(_missing))
