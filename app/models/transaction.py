from datetime import datetime
from app import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(256))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat(),
            'type': self.type,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }