from flask_restful import Resource, reqparse, inputs
from flask_api import status
from app.models import (
    CompetitionMeta as CompetitionMetaModel,
    SimilarityScores as SimilarityScoresModel
)


class CompetitionMeta(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('competition_id', required=True)
        data_payload = parser.parse_args()

        competition_meta = CompetitionMetaModel.find_by_competition_id(data_payload['competition_id'])
        return {'competition': competition_meta.competition,
                'teams': competition_meta.teams,
                'competitors': competition_meta.competitors,
                'categories': competition_meta.categories,
                'entries': competition_meta.entries}, \
               status.HTTP_200_OK

class SimilarityScores(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('competition_id', required=True)
        parser.add_argument('top_n')
        data_payload = parser.parse_args()
        competition = data_payload['competition_id']
        top_n = data_payload['top_n'] if data_payload['top_n'] else 50

        similarity_scores = SimilarityScoresModel.find_by_competition_id(data_payload['competition_id'], top_n)
        print(similarity_scores)
        return {'similarity_scores': list(map(lambda obj: obj.json(), similarity_scores))}, status.HTTP_200_OK

