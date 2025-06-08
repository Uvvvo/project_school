from app import app
from database import init_db

def initialize_database():
    with app.app_context():
        init_db()
        print("✅ تم تهيئة قاعدة البيانات بنجاح!")

if __name__ == '__main__':
    initialize_database()