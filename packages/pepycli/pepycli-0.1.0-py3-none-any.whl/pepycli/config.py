import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / ".env"

def load_config():
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)

    api_key = os.getenv("PEPY_API_KEY")

    if not api_key:
        api_key = input("Enter your PEPY API key: ").strip()

        with open(ENV_PATH, "w") as f:
            f.write(f"PEPY_API_KEY={api_key}\n")

    return {"API_KEY": api_key}

config = load_config()
