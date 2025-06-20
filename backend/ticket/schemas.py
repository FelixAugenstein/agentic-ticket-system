from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class Ticket(BaseModel):
    ticket_id: str
    name: str
    email: str
    problem_description: str
    category: str

# define DisplayProduct to only display certain entries
class DisplayTicket(BaseModel):
    ticket_id: str
    name: str
    email: str
    problem_description: str
    category: str
    model_config = ConfigDict(from_attributes=True)
    # class Config:
    #     orm_mode = True