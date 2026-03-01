from sqlalchemy import Column, Integer, String, JSON
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Text
from datetime import datetime, timezone
import os

# Use JSONB for PostgreSQL, JSON for SQLite (in tests)
JsonType = JSONB if os.environ.get("RUNNING_TESTS") != "1" else JSON

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    trees = relationship("TreeSession", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")

class TreeSession(Base):
    __tablename__ = "tree_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tree_data = Column(JsonType)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="trees")
    chats = relationship("ChatMessage", back_populates="tree", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    user_id = Column(Integer, ForeignKey("users.id"))
    tree_id = Column(Integer, ForeignKey("tree_sessions.id"))

    user = relationship("User", back_populates="chats")
    tree = relationship("TreeSession", back_populates="chats")

