"""File with settings and configs for the project"""

from envparse import Env
from jose.constants import ALGORITHMS

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)  # connect string for the database


SECRET_KEY = 'secret_key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30