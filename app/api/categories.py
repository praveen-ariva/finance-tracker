from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.category import Category
from app import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
@jwt_required()
def get_categories():
    current_user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200

@categories_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_category(id):
    current_user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    return jsonify({'category': category.to_dict()}), 200

@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Create new category
    category = Category(
        name=data['name'],
        description=data.get('description', ''),
        color=data.get('color', '#000000'),
        user_id=current_user_id
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201

@categories_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    current_user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if data.get('name'):
        category.name = data['name']
    if data.get('description') is not None:
        category.description = data['description']
    if data.get('color'):
        category.color = data['color']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200

@categories_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    current_user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200