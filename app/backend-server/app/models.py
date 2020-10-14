from app import db

class CompetitionMeta(db.Model):
    competition = db.Column(db.VARCHAR(255), primary_key=True)
    teams = db.Column(db.INTEGER)
    competitors = db.Column(db.INTEGER)
    entries = db.Column(db.INTEGER)
    competition_name = db.Column(db.VARCHAR(255))
    categories = db.Column(db.VARCHAR(255))

    def __repr__(self):
        return 'CometitionMeta Record'

    @classmethod
    def find_by_competition_id(cls, id):
        return cls.query.filter_by(competition=id).first()

    @classmethod
    def query_all(cls):
        return cls.query.distinct(cls.competition).all()

class SimilarityScores(db.Model):
    competitor = db.Column(db.VARCHAR(40), primary_key=True)
    competition = db.Column(db.VARCHAR(255), primary_key=True)
    kernel = db.Column(db.VARCHAR(255), primary_key=True)
    competitor2 = db.Column(db.VARCHAR(40), primary_key=True)
    kernel2 = db.Column(db.VARCHAR(255), primary_key=True)
    importedpackages = db.Column(db.TEXT)
    similarityscore = db.Column(db.FLOAT)

    def __repr__(self):
        return 'SimilarityScore Record'

    def json(self):
        return {'suspect': f'{self.competitor}/{self.kernel}',
                'victim': f'{self.competitor2}/{self.kernel2}',
                'packages': self.importedpackages,
                'similarity_score': self.similarityscore}

    @classmethod
    def find_by_competition_id(cls, id, top_n):
        return cls.query.filter_by(competition=id).order_by(SimilarityScores.similarityscore.desc()).limit(top_n).all()

    @classmethod
    def find_processed_competition(cls):
        competition_ids = list(map(lambda obj: obj.competition, cls.query.distinct(cls.competition).all()))
        return CompetitionMeta().query.filter(CompetitionMeta.competition.in_(competition_ids)).order_by(CompetitionMeta.competition.asc()).all()

