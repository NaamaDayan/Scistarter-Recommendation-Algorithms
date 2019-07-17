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
        'user_index': fields.Int(), #TODO:: should be string
        'k': fields.Int(),
        'algorithm_name': fields.Str(),
    })
    def get(self, user_index=None, k=3, algorithm_name='CFItemItem'):
        algorithm = eval(algorithm_name)(data_items)
        results = get_recommendations(user_index, k, algorithm)
        return jsonify(dict(
            user_index=user_index,
            k=k,
            algorithm_name=algorithm_name,
            recommendations=[int(i) for i in results]
        ))

api.add_resource(Algo, '/algo')

if __name__ == '__main__':
     app.run(port='8080')
