from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, FileField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])

class StudentForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    mother_name = StringField('اسم الأم', validators=[DataRequired()])
    birth_date = DateField('تاريخ الميلاد', validators=[DataRequired()])
    gender = SelectField('الجنس', choices=[('male', 'ذكر'), ('female', 'أنثى')], validators=[DataRequired()])
    student_type = SelectField('نوع الطالب', choices=[('registered', 'مسجل'), ('hosted', 'استضافة')], validators=[DataRequired()])
    profile_pic = FileField('صورة الطالب')
    class_name = StringField('الصف', validators=[DataRequired()])
    section = StringField('القسم', validators=[DataRequired()])
    academic_year = StringField('السنة الدراسية', validators=[DataRequired()])

class TeacherForm(FlaskForm):
    first_name = StringField('الاسم الأول', validators=[DataRequired()])
    second_name = StringField('اسم الأب', validators=[DataRequired()])
    third_name = StringField('اسم الجد', validators=[DataRequired()])
    birth_date = DateField('تاريخ الميلاد', validators=[DataRequired()])
    gender = SelectField('الجنس', choices=[('male', 'ذكر'), ('female', 'أنثى')], validators=[DataRequired()])
    profile_pic = FileField('صورة المعلم')
    qualification = StringField('الشهادة', validators=[DataRequired()])
    specialization = StringField('التخصص', validators=[DataRequired()])
    hiring_date = DateField('تاريخ التعيين', validators=[DataRequired()])
    years_experience = IntegerField('سنوات الخبرة', validators=[DataRequired()])
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('اسم المستخدم موجود مسبقاً')

class DeveloperUserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    role = SelectField('الصلاحية', choices=[
        ('developer', 'مطور'),
        ('admin', 'مدير'),
        ('teacher', 'معلم'),
        ('assistant', 'مساعد')
    ], validators=[DataRequired()])
    is_active = BooleanField('الحساب نشط', default=True)
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('اسم المستخدم موجود مسبقاً')