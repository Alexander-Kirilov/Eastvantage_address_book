from fastapi import FastAPI, HTTPException, Depends
from geopy import Nominatim
from geopy.distance import geodesic
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# get connection to the database
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Contact(BaseModel):
    country: str = Field(min_length=2)
    region: str = Field(min_length=1, max_length=20)
    city: str = Field(min_length=1, max_length=20)
    address: str = Field(min_length=1, max_length=20)


CONTACTS = []


# list all contacts
@app.get("/")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Contacts).all()


# create contact
@app.post("/")
def create_contact(contact: Contact, db: Session = Depends(get_db)):
    contact_model = models.Contacts()
    contact_model.country = contact.country
    contact_model.region = contact.region
    contact_model.city = contact.city
    contact_model.address = contact.address

    geolocator = Nominatim(user_agent="app")
    location = geolocator.geocode(contact.country + " " + contact.city + " " + contact.address)

    contact_model.latitude = location.latitude
    contact_model.longitude = location.longitude
    db.add(contact_model)
    db.commit()

    return contact


# update data in the database
@app.put("/{contact_id}")
def update_contact(contact_id: int, contact: Contact, db: Session = Depends(get_db)):
    contact_model = db.query(models.Contacts).filter(models.Contacts.id == contact_id).first()

    # check if the contact is in the database
    if contact_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {contact_id} : Does not exist"
        )

    contact_model.country = contact.country
    contact_model.region = contact.region
    contact_model.city = contact.city
    contact_model.address = contact.address
    # update location
    geolocator = Nominatim(user_agent="app")
    location = geolocator.geocode(contact.country + " " + contact.city + " " + contact.address)
    contact_model.latitude = location.latitude
    contact_model.longitude = location.longitude

    db.add(contact_model)
    db.commit()

    return contact


# delete contact
@app.delete("/{contact_id}")
def delete_book(contact_id: int, db: Session = Depends(get_db)):
    contact_model = db.query(models.Contacts).filter(models.Contacts.id == contact_id).first()

    # check if the contact is in the database
    if contact_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {contact_id} : Does not exist"
        )

    db.query(models.Contacts).filter(models.Contacts.id == contact_id).delete()

    db.commit()
    return {"message": "Contact is deleted!"}


# list all addresses from current distance
@app.get("/list_addresses/{contact_id}")
def retrieve_addresses(contact_id: int, distance: float, db: Session = Depends(get_db)):
    contact_model = db.query(models.Contacts).filter(models.Contacts.id == contact_id).first()

    # check if the contact is in the database
    if contact_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {contact_id} : Does not exist"
        )

    geolocator = Nominatim(user_agent="app")
    location = (int(contact_model.latitude), int(contact_model.longitude))
    locations = geolocator.reverse(location)
    addresses = []
    for loc in locations:
        if geodesic(location, loc).km <= distance:
            addresses.append(loc)
    return addresses
