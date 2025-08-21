from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), default="user")

class Rowingdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    leg_1 = db.Column(db.Float, nullable=False)
    leg_2 = db.Column(db.Float, nullable=False)
    leg_3 = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    avg_500m_time_in_secs = db.Column(db.Float, nullable=False)

    user = db.relationship("Users", backref=db.backref("rowing_entries", lazy=True))

    def __init__(self, user_id, leg_1, leg_2, leg_3, date=None):
        self.user_id = user_id
        self.leg_1 = leg_1
        self.leg_2 = leg_2
        self.leg_3 = leg_3
        self.total = round(leg_1 + leg_2 + leg_3)
        if date:
            self.date = date
        self.avg_500m_time_in_secs = (
            round((900 / self.total) * 500, 2) if self.total > 0 else 0
        )
