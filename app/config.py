from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ["DB_NAME"]
SECRET_KEY = os.environ["SECRET_KEY"]
RABBIT_USER = os.environ["RABBIT_USER"]
RABBIT_PWD = os.environ["RABBIT_PWD"]
RABBIT_PORT = os.environ["RABBIT_PORT"]
RABBIT_HOST = os.environ["RABBIT_HOST"]