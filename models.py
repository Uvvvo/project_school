from database import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(128))
    role = Column(Enum('developer', 'admin', 'teacher', 'assistant', name='user_roles'))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    profile_pic = Column(String(255), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150))
    mother_name = Column(String(100))
    birth_date = Column(Date)
    gender = Column(Enum('male', 'female', name='gender_types'))
    student_type = Column(Enum('registered', 'hosted', name='student_types'))
    profile_pic = Column(String(255), nullable=True)
    class_name = Column(String(50))
    section = Column(String(20))
    academic_year = Column(String(10))
    barcode_data = Column(String(50), unique=True)
    encrypted_data = Column(String(256))
    registration_date = Column(DateTime, server_default=func.now())

class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    first_name = Column(String(50))
    second_name = Column(String(50))
    third_name = Column(String(50))
    birth_date = Column(Date)
    gender = Column(Enum('male', 'female', name='gender_types'))
    qualification = Column(String(100))
    specialization = Column(String(100))
    hiring_date = Column(Date)
    years_experience = Column(Integer)
    profile_pic = Column(String(255))
    
    user = relationship("User")

class Attendance(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    scan_time = Column(DateTime)
    date = Column(Date)

class Grade(Base):
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    subject = Column(String(50))
    grade = Column(Float)
    exam_type = Column(String(50))
    notes = Column(String(255), nullable=True)
    date_recorded = Column(DateTime, default=func.now())
    teacher_id = Column(Integer)

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    code = Column(String(10), unique=True)

class TeacherSubject(Base):
    __tablename__ = 'teacher_subjects'
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    class_name = Column(String(50))
    section = Column(String(20))
    
    teacher = relationship("Teacher")
    subject = relationship("Subject")