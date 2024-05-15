from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL_ADDRESS")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the audit_changes function
# def audit_changes(target, operation, connection, mapper):
#     print(f"After {operation}: {target}: {connection}: {mapper}")

# # Listen for the 'after_insert', 'after_update', and 'after_delete' events
# @event.listens_for(Base, 'after_insert', propagate=True)
# def receive_after_insert(mapper, connection, target):
#     audit_changes(target, 'insert', connection, mapper)

# @event.listens_for(Base, 'after_update', propagate=True)
# def receive_after_update(mapper, connection, target):
#     audit_changes(target, 'update', connection, mapper)

# @event.listens_for(Base, 'after_delete', propagate=True)
# def receive_after_delete(mapper, connection, target):
#     audit_changes(target, 'delete', connection, mapper)