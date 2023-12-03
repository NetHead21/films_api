from sqlalchemy import Column, Integer, String
from database import Base


class Films(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    director = Column(String)
