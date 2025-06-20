from fastapi import APIRouter
from fastapi import FastAPI, status, Response, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi.params import Depends
from ..database import get_db
from ..import models, schemas
from typing import List



router = APIRouter(
    tags=['Tickets'],
    prefix="/ticket"
)

@router.delete('/{ticket_id}')
def delete(ticket_id, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).delete(synchronize_session=False)
    db.commit()
    return {'ticket deleted'}

@router.get('/all', response_model=List[schemas.DisplayTicket])
def tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets


@router.get('/{ticket_id}', response_model=schemas.DisplayTicket)
def ticket(ticket_id, db: Session = Depends(get_db)):
    #ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    ticket = db.query(models.Ticket)\
        .filter(models.Ticket.ticket_id == ticket_id)\
        .first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket not found')
    return ticket

@router.put('/{ticket_id}')
def update(ticket_id, request: schemas.Ticket, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id)
    if not ticket.first():
        pass
    ticket.update(request.model_dump())
    db.commit()
    return {'Ticket successfully updated'}


@router.post('', status_code=status.HTTP_201_CREATED)
def add(request: schemas.Ticket, db: Session = Depends(get_db)):
    new_ticket = models.Ticket(
        name=request.name, 
        email=request.email,
        problem_description=request.problem_description, 
        category=request.category,
        ticket_id=request.ticket_id)
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return request