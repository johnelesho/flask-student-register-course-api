from enum import unique
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET']= 'elesho'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studcourse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(11), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    courses = db.Column(db.String(100), nullable=True)
    is_couse_rep = db.Column(db.Boolean, default=False, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(5), unique=True, nullable=False)
    course_title = db.Column(db.String(50), unique=True, nullable=False)
    course_unit = db.Column(db.Integer, nullable=False, default=1)

# 


if __name__ == "__main__":
    app.run(debug=True)