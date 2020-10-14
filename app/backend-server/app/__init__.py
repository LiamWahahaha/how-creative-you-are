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
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.resources.api_resources import (
    Competition,
    CompetitionMeta,
    SimilarityScores
)

api.add_resource(Competition, '/api/competition/')
api.add_resource(CompetitionMeta, '/api/competition-meta/')
api.add_resource(SimilarityScores, '/api/similarity-scores/')

@app.route('/api')
def helloWorld():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
