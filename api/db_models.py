from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)
    email = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DistroVote(Base):
    __tablename__ = "distro_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    distro_name = Column(String, nullable=False)
    vote_type = Column(Integer, nullable=False) # 1 or -1
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DistroEdit(Base):
    __tablename__ = "distro_edits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    distro_name = Column(String, nullable=False)
    field = Column(String, nullable=False)
    new_value = Column(Text, nullable=False)
    status = Column(String, default="pending") # pending, approved, rejected
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
