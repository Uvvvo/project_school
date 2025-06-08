from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///school.db')
Session = sessionmaker(bind=engine)
db_session = Session()

def init_db():
    Base.metadata.create_all(engine)
    
    # إضافة المواد الدراسية الأساسية
    from models import Subject
    
    subjects = [
        {"name": "التربية الإسلامية", "code": "islamic"},
        {"name": "اللغة العربية", "code": "arabic"},
        {"name": "اللغة الانكليزية", "code": "english"},
        {"name": "الرياضيات", "code": "math"},
        {"name": "العلوم", "code": "science"},
        {"name": "الاجتماعيات", "code": "social"},
        {"name": "الفنية", "code": "art"},
        {"name": "الرياضة", "code": "sport"}
    ]
    
    for subject_data in subjects:
        if not db_session.query(Subject).filter_by(code=subject_data['code']).first():
            subject = Subject(**subject_data)
            db_session.add(subject)
    
    # إنشاء مستخدم مططور إذا لم يكن موجوداً
    from models import User
    if not db_session.query(User).filter_by(username='developer').first():
        developer = User(
            username='developer',
            role='developer',
            is_active=True
        )
        developer.set_password('devpassword')
        db_session.add(developer)
    
    db_session.commit()