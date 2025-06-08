import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///school.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/profile_pics'
    BARCODE_FOLDER = 'static/barcodes'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB