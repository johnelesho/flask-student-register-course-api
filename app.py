from enum import unique
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY']= os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studcourseapi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(50), unique= True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    courses = db.Column(db.String(100), nullable=True)
    is_team_lead = db.Column(db.Boolean, default=False, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(5), unique=True, nullable=False)
    course_title = db.Column(db.String(50), unique=True, nullable=False)
    course_unit = db.Column(db.Integer, nullable=False, default=1)



def get_authorization(f):
    @wraps(f)
    def decorator(*args, **kwargs):

      token = None

      if 'x-access-tokens' in request.headers:
         token = request.headers['x-access-tokens']

      if not token:
         return jsonify({'message': 'a valid token is missing'}), 401

      try:
         data = jwt.decode(token, app.config['SECRET_KEY'])
         current_student = Student.query.filter_by(reg_no=data['reg_no']).first() or Student.query.filter_by(username=data['username']).first()
      except:
         return jsonify({'message': 'token is invalid'}), 401

      return f(current_student, *args, **kwargs)
    return decorator


#Students Login to get the authorization
@app.route('/login')
def login():
    auth = request.authorization

# if there is no authentication information
    if not auth or not auth.username or not auth.password:
        return make_response('Login details not available', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

# if the authenticated details[username] is in the database 
    stud = Student.query.filter_by(username=auth.username).first() or Student.query.filter_by(reg_no=auth.username).first()
    print("student: ", stud)
    # if stud == None:
    #     stud = Student.query.filter_by(reg_no=auth.username).first()
    #     print("student: ", stud.username)
    if not stud:
         return make_response('Login Error, Check your username', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

# if the authenticated details[password] matches 
    if check_password_hash(stud.password, auth.password):
            token = jwt.encode({
                "reg_no": stud.reg_no, 
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            app.config['SECRET_KEY']
            )
            return jsonify({'token': token.decode('UTF-8')})

    return make_response('Login Error, Check your password', 401, {'WWW-Authentication': 'Basic realm="Login required"'})


# student route
@app.route('/student/', methods=['POST'])
@get_authorization
def create_new_student(current_student):
    # only team lead can create new student
    if not current_student.is_team_lead:
            return jsonify({"message": "Cannot perform that function"})

    data = request.get_json()
    # If username and password are not supplied
    if not 'username' in data or not 'password' in data:
         return jsonify({
        "message": "Incomplete Data",
        "Data" : [],
        "No of Registered Courses": []
        }), 401
    else:
        new_student_regno = str(uuid.uuid4())
        new_student_username = data['username']
        new_student_password= generate_password_hash(data['password'], method='sha256')

    if not 'courses' in data:
        new_student_courses = []
    else:
        new_student_courses = str(data['courses']).upper()
        
    if not 'is_team_lead' in data:
        new_student_team_lead = False
    else:
        new_student_team_lead =data['team_lead']

    new_student = Student(reg_no= new_student_regno, username=new_student_username, password=new_student_password, courses=new_student_courses, is_team_lead = new_student_team_lead)
    try:
        db.session.add(new_student)
        db.session.commit()
        message = "New Students Registered."
    except:
        message = "Could Not Register The Student."
    
    try:
        new_student = Student.query.filter_by(reg_no=new_student_regno).first()
        student_data = {}
        student_data['id'] = new_student.id
        student_data['reg_no'] = new_student.reg_no
        student_data['username'] = new_student.username
        student_data['password'] = new_student.password
        student_data['is_team_lead'] = new_student.is_team_lead
        
        if not 'courses' in new_student:
            student_data['courses'] = []
            no_courses = 0
        else:
            courses = new_student.courses.split(',')
            student_data['courses'] = [course.strip() for course in courses ]
            no_courses = len(student_data['courses'])
            
    except:
        message += " Could not Fetch student details"
        student_data={}
        no_courses = 0
        
    return jsonify({
    "message": message,
    "Data" : student_data,
    "No of Registered Courses": no_courses
    })




@app.route('/student/', methods=['GET'])
@get_authorization
def get_all_students(current_student):
    if not current_student.is_team_lead:
            return jsonify({"message": "Cannot perform that function"})
    students = Student.query.all()
    output=[]
    count =0
    if not students:
        message = "Could not Fetch student details"
    else:
        message = "List of Registered Students"
        count = len(students)
        for student in students:
            student_data = {}
            student_data['id'] = student.id
            student_data['reg_no'] = student.reg_no
            student_data['username'] = student.username
            student_data['password'] = student.password

            if student.courses==None:
                courses = []
            else:
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
@get_authorization
def get_one_student(current_student, stud_reg_no):
    if not current_student.is_team_lead:
            return jsonify({"message": "Cannot perform that function"})
    new_student = Student.query.filter_by(reg_no=stud_reg_no).first() or Student.query.filter_by(username=stud_reg_no).first()
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
@get_authorization
def make_student_team_lead(current_student, reg_no):
    if not current_student.is_team_lead:
            return jsonify({"message": "Cannot perform that function"})  
    student = Student.query.filter_by(reg_no=reg_no).first() or Student.query.filter_by(username=reg_no).first()
    if not student:
        message = "Could not Fetch student details"
           
    else:
        message = "Student now a team lead"
        student.is_team_lead = True
        db.session.commit()
       
        
    return jsonify({
    "message": message,
    
    })

@app.route('/student/courses', methods=['GET'])
@get_authorization
def get_student_courses( current_student):
    # if not current_student.is_team_lead:
    #         return jsonify({"message": "Cannot perform that function"})
    student = Student.query.filter_by(reg_no=current_student.reg_no).first()
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

@app.route('/student/courses', methods=['POST'])
@get_authorization
def register_student_courses(current_student):
    
    student = Student.query.filter_by(reg_no=current_student.reg_no).first()
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
            student = Student.query.filter_by(reg_no=current_student.reg_no).first()
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


@app.route('/student/courses', methods=['DELETE'])
@get_authorization
def delete_courses(current_student):
    
    student = Student.query.filter_by(reg_no=current_student.reg_no).first()
    if not student:
        message = "Could not Fetch student details"
        count = 0
        courses =[]
           
    else:
        courses = [course.strip().upper() for course in student.courses.split(',')]
        print(courses)
        # print(student.courses)
        data = request.get_json()
        count = len(courses)  
        if "courses" in data:
            new_courses = [course.strip().upper() for course in data['courses'].split(',')]
            data['courses'].split(',')
            
            # courses.append(new_courses)
            for c in new_courses:
                if c in courses:
                    courses.remove(c)
            
            courses_now = ",".join(courses)

            # # courses= [course.strip() for course in courses ]
            student.courses = courses_now
            # [].
            # count = len([course.strip() for course in courses ])
            
            db.session.commit()
            student = Student.query.filter_by(reg_no=current_student.reg_no).first()
            courses = [course.strip() for course in student.courses.split(',')]
            count = len(courses)
            message = "New Courses Registered by Student"
        else:
            message = "Courses to be removed not supplied, returning already registered courses"
        
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
@get_authorization
def remove_student(current_student, reg_no):
    if not current_student.is_team_lead:
            return jsonify({"message": "Cannot perform that function"})  
   
    student = Student.query.filter_by(reg_no=reg_no).first() or Student.query.filter_by(username=reg_no).first()
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
    # db.create_all()
    # # admin_user= Student(reg_no= "admin", username="admin", password=generate_password_hash("admin", method='sha256'), is_team_lead = True)
    # # db.session.add(admin_user)
    # # db.session.commit()
    app.run(debug=True)