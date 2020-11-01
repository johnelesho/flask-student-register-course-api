from enum import unique
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


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
    data = request.get_json()
    new_student_regno = data['reg_no']
    new_student_username = data['username']
    new_student_password= generate_password_hash(data['reg_no'], method='sha256')
    new_student_courses = str(data['courses']).upper()
    if not 'is_team_lead' in data:
        new_student_team_lead = False
    else:
        new_student_team_lead =data['team_lead']

    new_student = Student(reg_no= new_student_regno, username=new_student_username, password=new_student_password, courses=new_student_courses, is_team_lead = new_student_team_lead)
    try:
        db.session.add(new_student)
        db.session.commit()
        message = "New Students Registered"
    except:
        message = "Could Not Register The Student"
    
    new_student = Student.query.filter_by(reg_no=new_student_regno).first()
    if not new_student:
        message += "\n Could not Fetch student details"
        student_data={}

    student_data = {}
    student_data['id'] = new_student.id
    student_data['reg_no'] = new_student.reg_no
    student_data['username'] = new_student.username
    student_data['password'] = new_student.password
    courses = new_student.courses.split(',')
    student_data['courses'] = [course.strip() for course in courses ]
    student_data['is_team_lead'] = new_student.is_team_lead
    
    return jsonify({
    "message": message,
    "Data" : student_data,
    "No of Registered Courses": len(courses)
    })




@app.route('/student/', methods=['GET'])
def get_all_students():
    
    students = Student.query.all()
    output=[]
    if not students:
        message = "\n Could not Fetch student details"
    else:
        message = "List of Registered Students"
        count = len(students)
        for student in students:
            student_data = {}
            student_data['id'] = student.id
            student_data['reg_no'] = student.reg_no
            student_data['username'] = student.username
            student_data['password'] = student.password
            # if students.courses:
            courses = student.courses.split(',')
            student_data['courses'] = [course.strip() for course in courses ]
            student_data['is_team_lead'] = student.is_team_lead
            output.append(student_data)

    
    return jsonify({
    "message": message,
    "Data" : output,
    "Total Registered": count
    })



@app.route('/student/<stud_reg_no>', methods=['GET'])
def get_one_student(stud_reg_no):
    
    new_student = Student.query.filter_by(reg_no=stud_reg_no).first()
    if not new_student:
        message = "Could not Fetch student details"
        student_data={}
        courses=""
    else:
        message = "Student Details"
        student_data = {}
        student_data['id'] = new_student.id
        student_data['reg_no'] = new_student.reg_no
        student_data['username'] = new_student.username
        student_data['password'] = new_student.password
        courses = new_student.courses.split(',')
        student_data['courses'] = [course.strip() for course in courses ]
        student_data['is_team_lead'] = new_student.is_team_lead
        
    return jsonify({
    "message": message,
    "Data" : student_data,
    "No of Registered Courses": len(courses)
    })


@app.route('/student/<reg_no>', methods=['PUT'])
def make_student_team_lead(reg_no):
    
    student = Student.query.filter_by(reg_no=reg_no).first()
    if not student:
        message = "Could not Fetch student details"
           
    else:
        message = "Student now a team lead"
        student.is_team_lead = True
        db.session.commit()
       
        
    return jsonify({
    "message": message,
    
    })

@app.route('/student/<reg_no>/courses', methods=['GET'])
def get_student_courses(reg_no):
    
    student = Student.query.filter_by(reg_no=reg_no).first()
    if not student:
        message = "Could not Fetch student details"
        count = 0
        courses =[]
           
    else:
        message = "Courses Registered by Students"
        courses = student.courses.split(',')
        courses= [course.strip() for course in courses ]
        count = len(courses)
        
        
    return jsonify({
    "message": message,
    "Total Courses": count,
    "Courses" : courses
    
    })

@app.route('/student/<reg_no>/courses', methods=['POST'])
def register_student_courses(reg_no):
    
    student = Student.query.filter_by(reg_no=reg_no).first()
    if not student:
        message = "Could not Fetch student details"
        count = 0
        courses =[]
           
    else:
        courses = student.courses #.split(',')
        data = request.get_json()
        count = len(courses)  
        if "courses" in data:
            new_courses = data['courses']
            # courses.append(new_courses)
            courses += ","  + new_courses.upper() 
            # courses= [course.strip() for course in courses ]
            student.courses = str(courses)
            # count = len([course.strip() for course in courses ])
            
            db.session.commit()
            student = Student.query.filter_by(reg_no=reg_no).first()
            courses = [course.strip() for course in student.courses.split(',')]
            count = len(courses)
            message = "New Courses Registered by Student"
        else:
            message = "New Courses not supplied, returning already registered courses"
        
    return jsonify({
    "message": message,
    "Total Courses": count,
    "Courses" : courses
    
    })

# @app.route('/student/<reg_no>', methods=['PUT'])
# def remove_student_from_team_lead(reg_no):
    
#     student = Student.query.filter_by(reg_no=reg_no).first()
#     if not student:
#         message = "Could not Fetch student details"
           
#     else:
#         message = "Student removed from being a team lead"
#         student.is_team_lead = False
#         db.session.commit()
       
        
#     return jsonify({
#     "message": message,
    
#     })

# @app.route('/student/<reg_no>/<is_team_lead>', methods=['PUT'])
# def change_student_detail(reg_no, is_team_lead):
#     return ""

@app.route('/student/<reg_no>', methods=['DELETE'])
def remove_student(reg_no):
    student = Student.query.filter_by(reg_no=reg_no).first()
    if not student:
        message = "Could not Fetch student details"
    else:
        db.session.delete(student)
        db.session.commit()
        message = "Students details has been removed from the database"
       
        
        
    return jsonify({
    "message": message,
         
    })

    


# Course route
@app.route('/course/', methods=['POST'])
def create_new_course():
    return ""


@app.route('/course/', methods=['GET'])
def get_all_courses():
    return ""

@app.route('/course/<course_code>', methods=['GET'])
def get_one_course(course_code):
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