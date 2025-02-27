import os
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 불러오기
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
}

# JSON 설정 파일 로드
# with open("config.json", "r", encoding="utf-8") as f:
#     CONFIG = json.load(f)

# DEFAULT_MODEL = CONFIG["settings"]["default_model"]
# TEMPERATURE = CONFIG["settings"]["temperature"]
# MAX_TOKENS = CONFIG["settings"]["max_tokens"]