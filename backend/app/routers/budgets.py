from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Budget, User
from app.schemas import BudgetIn

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("")
def list_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Budget).filter(Budget.user_id == user.id).order_by(Budget.year.desc(), Budget.month.desc()).all()


@router.post("", status_code=201)
def create_budget(payload: BudgetIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(Budget).filter(Budget.user_id == user.id, Budget.category == payload.category, Budget.month == payload.month, Budget.year == payload.year).first()
    if existing:
        raise HTTPException(status_code=409, detail="Budget already exists for this category and month")
    row = Budget(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{budget_id}")
def update_budget(budget_id: int, payload: BudgetIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Budget not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(row)
    db.commit()
    return None
