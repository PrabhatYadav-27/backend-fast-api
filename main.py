from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


# initialize fastapi app
app = FastAPI()

# Database setup using sqllite
DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models

def get_timestamp():
    return datetime.utnow()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, unique=False, nullable=True)
    email = Column(String,  unique= False, nullable=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"),nullable=True) # link to another contact
    linkPrecedence = Column(Integer, nullable=False, default="primary") #   primary or  secondary
    createdAt = Column(DateTime, default=get_timestamp)
    updatedAt = Column(DateTime, default=get_timestamp, onupdate=get_timestamp)
    deletedAt = Column(DateTime, nullable=True)

    #Relationship to self (for the linked contact)
    primary_contact = relationship("Contact", remote_side=[id], backref="linked_contacts")

    # Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schema for request validation
class IdentifyRequest(BaseModel):
    email: EmailStr | None = None
    phoneNumber: str | None = None
