from dotenv import load_dotenv
import os

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

MAIL_USERNAME=os.getenv('MAIL_USERNAME')
MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
MAIL_FROM=os.getenv('MAIL_FROM')
MAIL_SERVER=os.getenv('MAIL_SERVER')
MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME')