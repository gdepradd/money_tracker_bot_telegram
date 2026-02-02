from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
import pytz

db = SQLAlchemy()

# Model Tabel Transaksi
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.BigInteger, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    transaction_type = db.Column(db.String(20)) # Expense / Income
    transaction_date = db.Column(db.DateTime, default=func.now())
    created_at = db.Column(db.DateTime, default=func.now())

    def to_dict(self):
        return {
            'item': self.item_name,
            'amount': self.amount,
            'date': self.transaction_date.strftime('%Y-%m-%d')
        }