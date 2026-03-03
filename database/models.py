from datetime import datetime
from sqlalchemy import DECIMAL, INT, DateTime, ForeignKey, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column



class Base(declarative_base()):
    __abstract__ = True


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
class Photos(Base):
    __tablename__ = 'photos'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(String(255), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    taken_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    width: Mapped[int] = mapped_column(INT, nullable=True)
    height: Mapped[int] = mapped_column(INT, nullable=True)


class Favorites(Base):
    __tablename__ = 'favorites'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey('photos.id'), primary_key=True)


class Comments(Base):
    __tablename__ = 'comments'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    photo_id: Mapped[int] = mapped_column(ForeignKey('photos.id'), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
       