import os
from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the absolute path of the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up one level to reach the 'backend' directory
backend_dir = os.path.dirname(current_dir)

# Construct the full path to 'ticket.db' in the 'backend' directory
db_path = os.path.join(backend_dir, 'ticket.db')

# Create the SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
    "check_same_thread": False
})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()