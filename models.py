from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    resistance = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"<User {self.name} - Resistance: {self.resistance}>"
