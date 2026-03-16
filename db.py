import os
import sys
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Find .env next to the EXE or next to the script
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(base_dir, ".env"))

_client = None

def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise ValueError("MONGO_URI not found. Make sure .env file is in the same folder as the EXE.")
        _client = MongoClient(uri, tlsCAFile=certifi.where())
    return _client["attendance_db"]


def students_col():
    return get_db()["students"]


def attendance_col():
    return get_db()["attendance"]
