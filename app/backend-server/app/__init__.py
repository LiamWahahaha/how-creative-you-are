import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS

from config import Config


app = Flask(__name__)
app.config.from_object(Config())
app.config['DEBUG'] = True
app.secret_key = os.urandom(24)
api = Api(app)
cors = CORS(app, resources={r'/*': {'origins"': '*'}})
    #'http://127.0.0.1:3000'}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.resources.api_resources import (
    CompetitionMeta,
    SimilarityScores
)

api.add_resource(CompetitionMeta, '/competition-meta')
api.add_resource(SimilarityScores, '/similarity-scores')

@app.route('/')
def helloWorld():
    return "Hello World!"

