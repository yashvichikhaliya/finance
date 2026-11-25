from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Transaction, User
from app.schemas import TransactionIn

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("")
def list_transactions(type: Optional[str] = None, category: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if type in ("income", "expense"):
        q = q.filter(Transaction.type == type)
    if category:
        q = q.filter(Transaction.category == category)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    return q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

@router.post("", status_code=201)
def create_transaction(payload: TransactionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = Transaction(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, payload: TransactionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(row)
    db.commit()
    return None
