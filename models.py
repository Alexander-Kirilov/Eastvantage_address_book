from sqlalchemy import Column, Integer, String, Float
from database import Base


class Contacts(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    region = Column(String)
    city = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
