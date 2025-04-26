from datetime import datetime, timedelta
from app.models.transaction import Transaction
from app.models.budget import Budget
from sqlalchemy import func
from app import db

def get_date_range(period):
    """Get start and end dates for different periods"""
    today = datetime.utcnow().date()
    
    if period == 'today':
        return today, today
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif period == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week, today
    elif period == 'this_month':
        start_of_month = today.replace(day=1)
        return start_of_month, today
    elif period == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        first_of_prev_month = last_of_prev_month.replace(day=1)
        return first_of_prev_month, last_of_prev_month
    elif period == 'this_year':
        start_of_year = today.replace(month=1, day=1)
        return start_of_year, today
    else:
        # Default to current month
        start_of_month = today.replace(day=1)
        return start_of_month, today

def get_spending_summary(user_id, start_date=None, end_date=None):
    """Get spending summary by category for a date range"""
    if not start_date:
        start_date = datetime.utcnow().date().replace(day=1)  # First day of current month
    if not end_date:
        end_date = datetime.utcnow().date()
    
    # Get expenses by category
    expenses_by_category = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Transaction.category_id).all()
    
    return expenses_by_category

def check_budget_status(user_id):
    """Check status of active budgets and return alerts for those close to or exceeding limits"""
    today = datetime.utcnow().date()
    
    # Get active budgets
    active_budgets = Budget.query.filter(
        Budget.user_id == user_id,
        Budget.start_date <= today,
        Budget.end_date >= today
    ).all()
    
    alerts = []
    
    for budget in active_budgets:
        # Calculate spending for this budget period
        spending = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            Transaction.date >= budget.start_date,
            Transaction.date <= budget.end_date
        ).scalar() or 0
        
        # Calculate percentage used
        percentage_used = (spending / budget.amount) * 100 if budget.amount > 0 else 0
        
        # Generate alerts based on percentage used
        if percentage_used >= 100:
            alerts.append({
                'budget_id': budget.id,
                'category_name': budget.category.name,
                'severity': 'high',
                'message': f'Budget for {budget.category.name} has been exceeded ({percentage_used:.1f}%)'
            })
        elif percentage_used >= 80:
            alerts.append({
                'budget_id': budget.id,
                'category_name': budget.category.name,
                'severity': 'medium',
                'message': f'Budget for {budget.category.name} is at {percentage_used:.1f}% of limit'
            })
    
    return alerts