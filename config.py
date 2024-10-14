from werkzeug.security import generate_password_hash

# config.py

hashed_password = generate_password_hash("@j0n_v3l4squ3z#")

class Config:
    SECRET_KEY = 'd9ddb8a50af95ba9a24052cb926e3b64ef04578fb6dc3d9b6ab9a13eec464195'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'jonathan.vr484@gmail.com'
    MAIL_PASSWORD = 'ycfs vvod evqw emwy'
    MAIL_DEFAULT_SENDER = 'jonathan.vr484@gmail.com'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
