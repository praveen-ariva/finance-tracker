from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app import db
from sqlalchemy import func

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('', methods=['GET'])
@jwt_required()
def get_budgets():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    category_id = request.args.get('category_id', type=int)
    
    # Base query
    query = Budget.query.filter_by(user_id=current_user_id)
    
    # Apply filters
    if active_only:
        today = datetime.utcnow().date()
        query = query.filter(Budget.start_date <= today, Budget.end_date >= today)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    budgets = query.all()
    
    # Enhance budget data with spending information
    result = []
    for budget in budgets:
        budget_dict = budget.to_dict()
        
        # Calculate current spending for this budget
        spending = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            Transaction.date >= budget.start_date,
            Transaction.date <= budget.end_date
        ).scalar() or 0
        
        budget_dict['spent'] = spending
        budget_dict['remaining'] = budget.amount - spending
        budget_dict['percentage_used'] = (spending / budget.amount) * 100 if budget.amount > 0 else 0
        
        result.append(budget_dict)
    
    return jsonify({'budgets': result}), 200

@budgets_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_budget(id):
    current_user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not budget:
        return jsonify({'message': 'Budget not found'}), 404
    
    # Calculate current spending for this budget
    spending = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user_id,
        Transaction.category_id == budget.category_id,
        Transaction.type == 'expense',
        Transaction.date >= budget.start_date,
        Transaction.date <= budget.end_date
    ).scalar() or 0
    
    budget_dict = budget.to_dict()
    budget_dict['spent'] = spending
    budget_dict['remaining'] = budget.amount - spending
    budget_dict['percentage_used'] = (spending / budget.amount) * 100 if budget.amount > 0 else 0
    
    return jsonify({'budget': budget_dict}), 200

@budgets_bp.route('', methods=['POST'])
@jwt_required()
def create_budget():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('amount') or not data.get('category_id') or not data.get('start_date') or not data.get('end_date'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Validate category
    category = Category.query.filter_by(id=data['category_id'], user_id=current_user_id).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
# Parse dates
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate date range
    if end_date < start_date:
        return jsonify({'message': 'End date must be after start date'}), 400
    
    # Create new budget
    budget = Budget(
        amount=float(data['amount']),
        start_date=start_date,
        end_date=end_date,
        category_id=data['category_id'],
        user_id=current_user_id
    )
    
    db.session.add(budget)
    db.session.commit()
    
    return jsonify({
        'message': 'Budget created successfully',
        'budget': budget.to_dict()
    }), 201

@budgets_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_budget(id):
    current_user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not budget:
        return jsonify({'message': 'Budget not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if data.get('amount'):
        budget.amount = float(data['amount'])
    
    if data.get('start_date'):
        try:
            budget.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid start date format. Use YYYY-MM-DD'}), 400
    
    if data.get('end_date'):
        try:
            budget.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid end date format. Use YYYY-MM-DD'}), 400
    
    # Validate date range
    if budget.end_date < budget.start_date:
        return jsonify({'message': 'End date must be after start date'}), 400
    
    if data.get('category_id'):
        category = Category.query.filter_by(id=data['category_id'], user_id=current_user_id).first()
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        budget.category_id = data['category_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Budget updated successfully',
        'budget': budget.to_dict()
    }), 200

@budgets_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_budget(id):
    current_user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not budget:
        return jsonify({'message': 'Budget not found'}), 404
    
    db.session.delete(budget)
    db.session.commit()
    
    return jsonify({'message': 'Budget deleted successfully'}), 200