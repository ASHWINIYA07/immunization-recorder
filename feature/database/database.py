import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "immunization.db")

def connect_db():
    return sqlite3.connect(DB_PATH)