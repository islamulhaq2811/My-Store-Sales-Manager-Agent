from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

MYSTORE_DB_HOST = os.getenv("MYSTORE_DB_HOST", "")
MYSTORE_DB_PORT = os.getenv("MYSTORE_DB_PORT", "3306")
MYSTORE_DB_USER = os.getenv("MYSTORE_DB_USER", "")
MYSTORE_DB_PASSWORD = os.getenv("MYSTORE_DB_PASSWORD", "")
MYSTORE_DB_NAME = os.getenv("MYSTORE_DB_NAME", "")

def is_mystore_configured():
    return all([MYSTORE_DB_HOST, MYSTORE_DB_USER, MYSTORE_DB_NAME])

_mystore_engine = None
_MystoreSession = None
_mystore_metadata = None

def get_mystore_engine():
    global _mystore_engine
    if _mystore_engine is None and is_mystore_configured():
        DATABASE_URL = f"mysql+pymysql://{MYSTORE_DB_USER}:{MYSTORE_DB_PASSWORD}@{MYSTORE_DB_HOST}:{MYSTORE_DB_PORT}/{MYSTORE_DB_NAME}"
        _mystore_engine = create_engine(DATABASE_URL)
    return _mystore_engine

def get_mystore_session():
    global _MystoreSession
    if _MystoreSession is None and is_mystore_configured():
        engine = get_mystore_engine()
        _MystoreSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _MystoreSession()

def get_mystore_metadata():
    global _mystore_metadata
    if _mystore_metadata is None and is_mystore_configured():
        engine = get_mystore_engine()
        _mystore_metadata = MetaData()
        _mystore_metadata.reflect(bind=engine)
    return _mystore_metadata

def get_mystore_tables():
    if not is_mystore_configured():
        return []
    metadata = get_mystore_metadata()
    return list(metadata.tables.keys())

def get_table_columns(table_name):
    if not is_mystore_configured():
        return []
    metadata = get_mystore_metadata()
    table = metadata.tables.get(table_name)
    if table is None:
        return []
    return [{"name": col.name, "type": str(col.type)} for col in table.columns]

def get_mystore_db():
    if not is_mystore_configured():
        return None
    db = get_mystore_session()
    try:
        yield db
    finally:
        db.close()
