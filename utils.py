import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app

def save_profile_picture(file, folder):
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    
    upload_folder = os.path.join(current_app.static_folder, 'profile_pics', folder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    filepath = os.path.join(upload_folder, new_filename)
    
    img = Image.open(file)
    img.thumbnail((500, 500))
    img.save(filepath)
    
    return f"profile_pics/{folder}/{new_filename}"

def delete_profile_picture(pic_path):
    if pic_path:
        full_path = os.path.join(current_app.static_folder, pic_path)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting profile picture: {e}")

def generate_secure_barcode(barcode_data, student_id):
    import barcode
    from barcode.writer import ImageWriter
    
    code = barcode.get('code128', barcode_data, writer=ImageWriter())
    
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
    
    filename = f"static/barcodes/{student_id}"
    code.save(filename)