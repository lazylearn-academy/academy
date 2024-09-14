from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ["DB_NAME"]
SECRET_KEY = os.environ["SECRET_KEY"]
RABBIT_USER = os.environ["RABBIT_USER"]
RABBIT_PWD = os.environ["RABBIT_PWD"]
RABBIT_PORT = os.environ["RABBIT_PORT"]
RABBIT_HOST = os.environ["RABBIT_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PWD = os.environ["DB_PWD"]
DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_PORT = os.environ["DB_PORT"]
POST_USER = os.environ["POST_USER"]
POST_PWD = os.environ["POST_PWD"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]