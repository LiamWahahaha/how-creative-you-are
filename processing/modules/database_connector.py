import os
from pyspark.sql import DataFrameWriter

class PostgresConnector:
    def __init__(self):
        self.database_name = self.get_env_variable('POSTGRES_DB')
        self.hostname = self.get_env_variable('POSTGRES_HOSTNAME')
        self.port = self.get_env_variable('POSTGRES_PORT')
        self.user = self.get_env_variable('POSTGRES_USER')
        self.password = self.get_env_variable('POSTGRES_PW')
        self.url_connect = "jdbc:postgresql://{hostname}:{self.port}/{self.database_name}"
        self.properties = {"user":self.user,
                           "password":self.password,
                           "driver": "org.postgresql.Driver"}

    def get_env_variable(self, name):
        try:
            return os.environ[name]
        except KeyError:
            message = f'Expected environment variable {name} not set.'
            raise Exxception(message)

    def get_writer(self, dataframe):
        return DataFrameWriter(dataframe)

    def write(self, dataframe, table, mode):
        db_writer = self.get_writer(dataframe)
        dbb_writer.jdbc(self.url_connect, table, mode, self.properties)

