from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
DB_USER = os.environ["DB_USER"]
DB_PWD = os.environ["DB_PWD"]
DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_PORT = os.environ["DB_PORT"]
POST_USER = os.environ["POST_USER"]
POST_PWD = os.environ["POST_PWD"]
SHOULD_CREATE_DB = os.environ["SHOULD_CREATE_DB"]
ENV = os.environ["ENV"]
PROD_HOST = os.environ["PROD_HOST"]
DEV_HOST = os.environ["DEV_HOST"]