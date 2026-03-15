import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise ValueError("MONGO_URI not set in .env file")
        _client = MongoClient(uri)
    return _client["attendance_db"]


def students_col():
    return get_db()["students"]


def attendance_col():
    return get_db()["attendance"]
