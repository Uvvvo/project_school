from app import app
from database import db_session
from models import User

with app.app_context():
    users = db_session.query(User).all()
    print(f"عدد المستخدمين: {len(users)}")
    for user in users:
        print(f"المستخدم: {user.username} - الصلاحية: {user.role}")