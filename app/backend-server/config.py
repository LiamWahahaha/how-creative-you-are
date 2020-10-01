import os

class Config(object):
    def __init__(self):
        POSTGRES_URL = self.get_env_variable('POSTGRES_URL')
        POSTGRES_USER = self.get_env_variable('POSTGRES_USER')
        POSTGRES_PASSWORD = self.get_env_variable('POSTGRES_PW')
        POSTGRES_DB = self.get_env_variable('POSTGRES_DB')
        DB_URL = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URL}/{POSTGRES_DB}'
        self.SQLALCHEMY_DATABASE_URI = DB_URL
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

    def get_env_variable(self, name):
        try:
            return os.environ[name]
        except KeyError:
            message = f'Expected environment variable {name} not set.'
            raise Exception(message)


