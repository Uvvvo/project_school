from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import uuid
from models import User, Student, Teacher, Attendance, Grade, Subject, TeacherSubject
from database import init_db, db_session
from forms import LoginForm, StudentForm, TeacherForm
from utils import save_profile_picture, delete_profile_picture, generate_secure_barcode
from encryption import encrypt_data, decrypt_data
from werkzeug.exceptions import abort


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

# Initialize database
init_db()

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    if current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ------ نظام الباركود والحضور ------
@app.route('/generate_barcodes')
@login_required
def generate_barcodes():
    students = Student.query.all()
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
    
    for student in students:
        code = barcode.get('code128', student.barcode_data, writer=ImageWriter())
        filename = f"static/barcodes/{student.id}"
        code.save(filename)
    
    return "تم إنشاء الباركود لجميع الطلاب"

@app.route('/scan_attendance', methods=['POST'])
@login_required
def scan_attendance():
    barcode_data = request.form.get('barcode')
    student = Student.query.filter_by(barcode_data=barcode_data).first()
    
    if student:
        new_attendance = Attendance(
            student_id=student.id,
            scan_time=datetime.now(),
            date=datetime.now().date()
        )
        db_session.add(new_attendance)
        db_session.commit()
        return jsonify({'status': 'success', 'student': student.full_name})
    
    return jsonify({'status': 'error', 'message': 'باركود غير صحيح'})

@app.route('/attendance')
@login_required
def attendance():
    today = datetime.now().date()
    attendance_records = Attendance.query.filter_by(date=today).all()
    return render_template('attendance.html', attendance_records=attendance_records)

# ------ نظام الدرجات ------
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    return render_template('teacher/dashboard.html', teacher=teacher)

@app.route('/teacher/grades', methods=['GET', 'POST'])
@login_required
def grades_entry():
    if current_user.role != 'teacher':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    return render_template('teacher/grades_entry.html', teacher=teacher)

@app.route('/get_students')
@login_required
def get_students():
    class_name = request.args.get('class_name')
    section = request.args.get('section')
    
    students = Student.query.filter_by(
        class_name=class_name, 
        section=section
    ).order_by(Student.full_name).all()
    
    students_list = []
    for student in students:
        students_list.append({
            'id': student.id,
            'full_name': student.full_name,
            'class_name': student.class_name,
            'section': student.section
        })
    
    return jsonify(students_list)

@app.route('/save_grades', methods=['POST'])
@login_required
def save_grades():
    subject = request.form.get('subject')
    class_name = request.form.get('class_name')
    section = request.form.get('section')
    exam_type = request.form.get('exam_type')
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    for key, value in request.form.items():
        if key.startswith('grade_'):
            student_id = key.split('_')[1]
            grade_value = value.strip()
            notes = request.form.get(f'notes_{student_id}', '').strip()
            
            if grade_value:
                try:
                    grade_value = float(grade_value)
                except ValueError:
                    continue
                
                if 0 <= grade_value <= 100:
                    new_grade = Grade(
                        student_id=student_id,
                        subject=subject,
                        grade=grade_value,
                        exam_type=exam_type,
                        notes=notes,
                        date_recorded=datetime.now(),
                        teacher_id=teacher.id
                    )
                    db_session.add(new_grade)
    
    db_session.commit()
    flash('تم حفظ الدرجات بنجاح', 'success')
    return redirect(url_for('grades_entry'))

@app.route('/teacher/view_grades')
@login_required
def view_grades():
    if current_user.role != 'teacher':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    subject = request.args.get('subject')
    class_name = request.args.get('class_name')
    section = request.args.get('section')
    exam_type = request.args.get('exam_type')
    
    query = Grade.query.filter_by(teacher_id=teacher.id)
    
    if subject:
        query = query.filter(Grade.subject == subject)
    if class_name:
        students = Student.query.filter_by(class_name=class_name).all()
        student_ids = [s.id for s in students]
        query = query.filter(Grade.student_id.in_(student_ids))
    if section:
        students = Student.query.filter_by(section=section).all()
        student_ids = [s.id for s in students]
        query = query.filter(Grade.student_id.in_(student_ids))
    if exam_type:
        query = query.filter(Grade.exam_type == exam_type)
    
    grades = query.order_by(
        Grade.date_recorded.desc()
    ).all()
    
    # إضافة معلومات الطالب لكل درجة
    for grade in grades:
        grade.student = Student.query.get(grade.student_id)
    
    return render_template('teacher/grades_view.html', grades=grades, teacher=teacher)

# ------ واجهة المطور والإدارة ------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role not in ['admin', 'assistant', 'developer']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    return render_template('admin/dashboard.html', 
                          student_count=student_count, 
                          teacher_count=teacher_count)

@app.route('/admin/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role not in ['admin', 'assistant', 'developer']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    form = StudentForm()
    
    if form.validate_on_submit():
        profile_pic = None
        if form.profile_pic.data:
            profile_pic = save_profile_picture(form.profile_pic.data, 'students')
        
        student_data = f"{form.full_name.data}|{form.class_name.data}|{form.section.data}"
        encrypted_data = encrypt_data(student_data)
        barcode_data = str(uuid.uuid4())
        
        student = Student(
            full_name=form.full_name.data,
            mother_name=form.mother_name.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            student_type=form.student_type.data,
            class_name=form.class_name.data,
            section=form.section.data,
            academic_year=form.academic_year.data,
            encrypted_data=encrypted_data,
            barcode_data=barcode_data,
            profile_pic=profile_pic
        )
        
        db_session.add(student)
        db_session.commit()
        
        generate_secure_barcode(barcode_data, student.id)
        
        flash('تمت إضافة الطالب بنجاح', 'success')
        return redirect(url_for('view_student', student_id=student.id))
    
    return render_template('admin/student_form.html', form=form)

@app.route('/admin/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role not in ['admin', 'developer']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    form = TeacherForm()
    
    if form.validate_on_submit():
        profile_pic = None
        if form.profile_pic.data:
            profile_pic = save_profile_picture(form.profile_pic.data, 'teachers')
        
        user = User(
            username=form.username.data,
            role='teacher'
        )
        user.set_password(form.password.data)
        db_session.add(user)
        db_session.commit()
        
        teacher = Teacher(
            user_id=user.id,
            first_name=form.first_name.data,
            second_name=form.second_name.data,
            third_name=form.third_name.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            qualification=form.qualification.data,
            specialization=form.specialization.data,
            hiring_date=form.hiring_date.data,
            years_experience=form.years_experience.data,
            profile_pic=profile_pic
        )
        
        db_session.add(teacher)
        db_session.commit()
        
        flash('تمت إضافة المعلم بنجاح', 'success')
        return redirect(url_for('view_teacher', teacher_id=teacher.id))
    
    return render_template('admin/teacher_form.html', form=form)

@app.route('/admin/student/<int:student_id>')
@login_required
def view_student(student_id):
    if current_user.role not in ['admin', 'assistant', 'developer']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    student = Student.query.get_or_404(student_id)
    return render_template('admin/view_student.html', student=student)

@app.route('/admin/teacher/<int:teacher_id>')
@login_required
def view_teacher(teacher_id):
    if current_user.role not in ['admin', 'developer']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    teacher = Teacher.query.get_or_404(teacher_id)
    user = User.query.get(teacher.user_id)
    return render_template('admin/view_teacher.html', teacher=teacher, user=user)

if __name__ == '__main__':
    app.run(debug=True)