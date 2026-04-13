from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)  # paper, video, blog
    link = Column(String)
    status = Column(String)  # to_learn, learning, completed
    tags = Column(String)  # comma-separated or JSON
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)  # Markdown
    tags = Column(String)
    linked_resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    linked_resource = relationship("Resource")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    status = Column(String)  # pending, completed
    priority = Column(String)  # low, medium, high
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)