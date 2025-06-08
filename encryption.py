from cryptography.fernet import Fernet
import base64
from flask import current_app

# مفتاح تشفير صالح (يجب تغييره في البيئة الإنتاجية)
FERNET_KEY = b'ha5IWhB18ufZ7npSfp8dbd-AM8NCv1qryz8gDM3UQQE='  # 32 بايت

class Encryption:
    def __init__(self):
        # التحقق من صحة المفتاح
        try:
            self.cipher_suite = Fernet(FERNET_KEY)
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")
    
    def encrypt_data(self, data):
        try:
            return self.cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            current_app.logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            current_app.logger.error(f"Decryption error: {e}")
            return None

# إنشاء نسخة من Encryption
encryption = Encryption()

def encrypt_data(data):
    return encryption.encrypt_data(data)

def decrypt_data(encrypted_data):
    return encryption.decrypt_data(encrypted_data)