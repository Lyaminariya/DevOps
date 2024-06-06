import os

# My configs

SECRET_KEY = os.getenv("SECRET_KEY")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "lyamkin200603@gmail.com"
MAIL_PASSWORD = "tqasvqsyzqytsnqf"

UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}