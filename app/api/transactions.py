from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models.transaction import Transaction
from app.models.category import Category
from app import db

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    
    # Get query parameters for filtering
    category_id = request.args.get('category_id', type=int)
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Transaction.query.filter_by(user_id=current_user_id)
    
    # Apply filters if provided
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(type=transaction_type)
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({'message': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({'message': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    # Order by date (newest first)
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return jsonify({
        'transactions': [transaction.to_dict() for transaction in transactions]
    }), 200

@transactions_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    return jsonify({'transaction': transaction.to_dict()}), 200

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('amount') or not data.get('type') or not data.get('category_id'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Validate transaction type
    if data['type'] not in ['income', 'expense']:
        return jsonify({'message': 'Transaction type must be either "income" or "expense"'}), 400
    
    # Validate category
    category = Category.query.filter_by(id=data['category_id'], user_id=current_user_id).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    # Parse date if provided
    transaction_date = datetime.utcnow().date()
    if data.get('date'):
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Create new transaction
    transaction = Transaction(
        amount=float(data['amount']),
        description=data.get('description', ''),
        date=transaction_date,
        type=data['type'],
        category_id=data['category_id'],
        user_id=current_user_id
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction': transaction.to_dict()
    }), 201

@transactions_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if data.get('amount'):
        transaction.amount = float(data['amount'])
    if data.get('description') is not None:
        transaction.description = data['description']
    if data.get('date'):
        try:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if data.get('type'):
        if data['type'] not in ['income', 'expense']:
            return jsonify({'message': 'Transaction type must be either "income" or "expense"'}), 400
        transaction.type = data['type']
    if data.get('category_id'):
        category = Category.query.filter_by(id=data['category_id'], user_id=current_user_id).first()
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        transaction.category_id = data['category_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction updated successfully',
        'transaction': transaction.to_dict()
    }), 200

@transactions_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted successfully'}), 200

@transactions_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_transaction_summary():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Transaction.query.filter_by(user_id=current_user_id)
    
    # Apply date filters if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({'message': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({'message': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    # Get all transactions within the filter
    transactions = query.all()
    
    # Calculate summary
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net = total_income - total_expense
    
    # Group by category
    category_summary = {}
    for t in transactions:
        category_name = t.category.name
        if category_name not in category_summary:
            category_summary[category_name] = {
                'income': 0,
                'expense': 0
            }
        category_summary[category_name][t.type] += t.amount
    
    return jsonify({
        'summary': {
            'total_income': total_income,
            'total_expense': total_expense,
            'net': net,
            'by_category': category_summary
        }
    }), 200