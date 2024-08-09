from sqlalchemy import Column, String
from database import Base

class Room(Base):
    __tablename__ = "rooms"

    name = Column(String, primary_key=True, index=True)
