from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Models
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(130), nullable=False, unique=True)
    phone_number = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120))
    address = db.Column(db.String(150))

    def __repr__(self):
        return f'{self.name} - {self.phone_number}'

