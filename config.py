from neomodel import config
import os

config.DATABASE_URL = os.environ["DATABASE_URL"]

SECRET_KEY = os.environ["SECRET_KEY"]  # Change this to a strong secret key
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Change this to a strong JWT secret key
