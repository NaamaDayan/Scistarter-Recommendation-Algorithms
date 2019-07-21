from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from webargs.flaskparser import use_kwargs
from webargs import fields
from datetime import datetime
from Recommender import *

app = Flask(__name__)
api = Api(app)

class Algo(Resource):
    @use_kwargs({
        'user_profile_id': fields.Str(),
        'k': fields.Int(),
    })
    def get(self, user_profile_id=None, k=3):
        algorithm = map_user_algorithm(user_profile_id)
        results = get_recommendations(user_profile_id, k, algorithm)
        return jsonify(dict(
            user_profile_id=user_profile_id,
            k=k,
            recommendations=[int(i) for i in results]
        ))

api.add_resource(Algo, '/algo')

if __name__ == '__main__':
    import sys
    argv = sys.argv + [None, None]
    host = str(argv[1]) if argv[1] else '127.0.0.1'
    port = int(argv[2]) if argv[2] else 8080
    app.run(port=port, host=host)
