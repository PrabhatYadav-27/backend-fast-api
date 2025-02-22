from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base


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


# API Endpoint
@app.post("/identify")
def identify_contact(request: IdentifyRequest):
    db = SessionLocal()
    try:
        email = request.email
        phone_number = request.phoneNumber

        # Fetch contacts matching email or phone number
        matching_contacts = db.query(Contact).filter(
            (Contact.email == email) | (Contact.phoneNumber == phone_number)
        ).all()
        
        if not matching_contacts:
            # No match found, create a new primary contact
            new_contact = Contact(email=email, phoneNumber=phone_number, linkPrecedence="primary")
            db.add(new_contact)
            db.commit()
            db.refresh(new_contact)
            return format_response(new_contact, [])
        
        # Find the primary contact
        primary_contact = None
        secondary_contacts = []
        
        for contact in matching_contacts:
            if contact.linkPrecedence == "primary":
                primary_contact = contact
            else:
                secondary_contacts.append(contact)
        
        # If no primary contact exists, make the first match primary
        if not primary_contact:
            primary_contact = matching_contacts[0]
            primary_contact.linkPrecedence = "primary"
            db.commit()
            db.refresh(primary_contact)
        
        # Check if the incoming contact details already exist as a secondary contact
        existing_secondary = db.query(Contact).filter(
            (Contact.email == email) | (Contact.phoneNumber == phone_number),
            Contact.linkPrecedence == "secondary"
        ).first()
        
        if not existing_secondary:
            # Create new secondary contact
            new_secondary = Contact(
                email=email,
                phoneNumber=phone_number,
                linkedId=primary_contact.id,
                linkPrecedence="secondary"
            )
            db.add(new_secondary)
            db.commit()
            db.refresh(new_secondary)
            secondary_contacts.append(new_secondary)
        
        return format_response(primary_contact, secondary_contacts)
    finally:
        db.close()

# Helper function to format response
def format_response(primary_contact, secondary_contacts):
    return {
        "primaryContactId": primary_contact.id,
        "emails": list(set([c.email for c in [primary_contact] + secondary_contacts if c.email])) ,
        "phoneNumbers": list(set([c.phoneNumber for c in [primary_contact] + secondary_contacts if c.phoneNumber])) ,
        "secondaryContactIds": [c.id for c in secondary_contacts]
    }