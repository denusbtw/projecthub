from .base import *


DATABASES = {"default": env.db("PROD_DATABASE_URL")}
