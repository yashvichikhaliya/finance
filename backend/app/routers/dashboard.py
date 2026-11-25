from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Transaction, User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today(); month_start = today.replace(day=1)
    rows = db.query(Transaction).filter(Transaction.user_id == user.id, Transaction.date >= month_start, Transaction.date <= today).all()
    income = sum(t.amount for t in rows if t.type == "income")
    expense = sum(t.amount for t in rows if t.type == "expense")
    categories = {}
    for t in rows:
        if t.type == "expense": categories[t.category] = categories.get(t.category, 0) + t.amount
    recent = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.desc(), Transaction.id.desc()).limit(5).all()
    return {"month": today.month, "year": today.year, "income": income, "expense": expense, "net": income-expense, "category_spending": categories, "recent_transactions": recent}
