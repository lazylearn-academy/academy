from dotenv import load_dotenv
import os

load_dotenv()

POST_USER = os.environ["POST_USER"]
POST_PWD = os.environ["POST_PWD"]
RABBIT_USER = os.environ["RABBIT_USER"]
RABBIT_PWD = os.environ["RABBIT_PWD"]
RABBIT_PORT = os.environ["RABBIT_PORT"]
RABBIT_HOST = os.environ["RABBIT_HOST"]