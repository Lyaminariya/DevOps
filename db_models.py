from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# All my models for DB


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    profile = db.relationship("Profile", backref="user", uselist=False)
    comment = db.relationship("Comment", backref="user")
    case = db.relationship("Case", backref="user")
    item = db.relationship("Item", backref="user")


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    email = db.Column(db.String(40))
    avatar_href = db.Column(db.String(50))


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    image_path = db.Column(db.String(100))
    items = db.relationship("Item", backref="case", cascade="all, delete-orphan")
    comment = db.relationship("Comment", backref="case")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    image_path = db.Column(db.String(100))
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("case.id"), nullable=False)
