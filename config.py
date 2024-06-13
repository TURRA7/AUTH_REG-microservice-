"""Application Configuration Module."""

import os
from dotenv import load_dotenv


load_dotenv()


PG_USER = os.environ.get("PG_USER")
PG_PASS = os.environ.get("PG_PASS")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
PG_DB = os.environ.get("PG_DB")
WOKR_EMAIL = os.environ.get("WOKR_EMAIL")
WOKR_EMAIL_PASS = os.environ.get("WOKR_EMAIL_PASS")
WORK_HOSTNAME = os.environ.get("WORK_HOSTNAME")
WOKR_PORT = os.environ.get("WOKR_PORT")
SECRET_KEY = os.environ.get("SECRET_KEY")
