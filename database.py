from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path
from contextlib import contextmanager

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "sales_manager")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

MYSTORE_DB_HOST = os.getenv("MYSTORE_DB_HOST", "")
MYSTORE_DB_PORT = os.getenv("MYSTORE_DB_PORT", "3306")
MYSTORE_DB_USER = os.getenv("MYSTORE_DB_USER", "")
MYSTORE_DB_PASSWORD = os.getenv("MYSTORE_DB_PASSWORD", "")
MYSTORE_DB_NAME = os.getenv("MYSTORE_DB_NAME", "")

_mystore_engine = None
_MystoreSessionLocal = None

def is_mystore_configured():
    return all([MYSTORE_DB_HOST, MYSTORE_DB_USER, MYSTORE_DB_NAME])

def get_mystore_engine():
    global _mystore_engine
    if _mystore_engine is None and is_mystore_configured():
        url = f"mysql+pymysql://{MYSTORE_DB_USER}:{MYSTORE_DB_PASSWORD}@{MYSTORE_DB_HOST}:{MYSTORE_DB_PORT}/{MYSTORE_DB_NAME}"
        _mystore_engine = create_engine(url)
    return _mystore_engine

def get_mystore_session():
    global _MystoreSessionLocal
    if _MystoreSessionLocal is None and is_mystore_configured():
        _MystoreSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_mystore_engine())
    return _MystoreSessionLocal() if _MystoreSessionLocal else None

@contextmanager
def mystore_session_scope():
    db = get_mystore_session()
    if db is None:
        yield None
        return
    try:
        yield db
    finally:
        db.close()

def get_mystore_db():
    return get_mystore_session()
