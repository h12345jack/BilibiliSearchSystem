from flask import Flask
from flask_restful import Resource, Api
from flask.ext.restful import reqparse

from whoosh_index import query

app = Flask(__name__)
api = Api(app)

todos = {}

class QueryAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('query_data', type = str, required = True,
            help = 'No task title provided', location = 'json')
        super(TaskListAPI, self).__init__()



api.add_resource(QueryAPI, '/<string:query>')

if __name__ == '__main__':
    app.run(debug=True)