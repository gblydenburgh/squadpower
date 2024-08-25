from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    resistance = db.Column(db.Integer, nullable=False)
    squads = db.relationship('Squad', backref='user', lazy=True)

class Squad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    power = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
