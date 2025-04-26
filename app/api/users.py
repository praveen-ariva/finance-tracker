from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Check if username is being updated and if it's already taken
    if data.get('username') and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 409
        user.username = data['username']
    
    # Check if email is being updated and if it's already taken
    if data.get('email') and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 409
        user.email = data['email']
    
    # Update password if provided
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@users_bp.route('/me/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Missing current_password or new_password'}), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'message': 'Current password is incorrect'}), 401
    
    # Set new password
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200