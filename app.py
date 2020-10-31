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
    is_team_lead = db.Column(db.Boolean, default=False, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(5), unique=True, nullable=False)
    course_title = db.Column(db.String(50), unique=True, nullable=False)
    course_unit = db.Column(db.Integer, nullable=False, default=1)

# student route
@app.route('/student/', methods=['POST'])
def create_new_student():
    return ""


@app.route('/student/', methods=['GET'])
def get_all_students():
    return ""

@app.route('/student/', methods=['GET'])
def get_one_student():
    return ""

@app.route('/student/<reg_no>', methods=['PUT'])
def change_student_detail(reg_no):
    return ""

@app.route('/student/<reg_no>/<is_team_lead>', methods=['PUT'])
def change_student_detail(reg_no, is_team_lead):
    return ""

@app.route('/student/<reg_no>', methods=['DELETE'])
def remove_student(reg_no):
    return ""


# Course route
@app.route('/student/', methods=['POST'])
def create_new_student():
    return ""


@app.route('/student/', methods=['GET'])
def get_all_courses():
    return ""

@app.route('/course/', methods=['GET'])
def get_one_course():
    return ""

@app.route('/course/<course_code>', methods=['PUT'])
def change_course_details(course_code):
    return ""

@app.route('/course/<course_code>', methods=['DELETE'])
def remove_course(course_code):
    return ""

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)