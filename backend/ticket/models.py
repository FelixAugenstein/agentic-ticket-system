from sqlalchemy import Column, Integer, String
from .database import Base
from datetime import date


class Ticket(Base):
    __tablename__ = 'tickets'
    ticket_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    problem_description = Column(String, nullable=False)
    category = Column(String, nullable=False)
