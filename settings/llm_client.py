import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def load_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    return OpenAI(api_key=api_key)
