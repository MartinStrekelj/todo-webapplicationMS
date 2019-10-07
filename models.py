import os
from sqlalchemy_wrapper import SQLAlchemy


db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite")) #connector

#Entity(tables):

class User(db.Model):

    id      = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique=True, nullable = False)
    email = db.Column(db.String, unique=True, nullable = False)
    password = db.Column(db.String(30), nullable = False)
    session_token = db.Column(db.String)
    # lists = db.relationship("List", backref=db.backref('User', lazy=True))
    lists = db.relationship("List")

class List(db.Model):

    id       = db.Column(db.Integer, primary_key= True)
    list_name = db.Column(db.String(30), nullable = False)
    uid = db.Column(db.Integer, db.ForeignKey(User.id), nullable= False)
    items = db.relationship("Item")




class Item(db.Model):

    id      = db.Column(db.Integer, primary_key = True)
    title    = db.Column(db.String(30), nullable = False)
    deadline = db.Column(db.String(30), nullable = False)
    text     = db.Column(db.String, nullable = False)
    active   = db.Column(db.Boolean(30), nullable = False)
    lid      = db.Column(db.Integer, db.ForeignKey(List.id),nullable=False)
    # lid      = db.relationship(db.Integer, db.ForeignKey(List.id))

