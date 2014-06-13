import json
from datetime import datetime
from datetime import date, timedelta
from flask import Flask, request, jsonify
from bson.json_util import dumps
from bson import json_util
from pymongo import MongoClient
from flask.ext.httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()

app = Flask(__name__)

client = MongoClient()
db = client['testdb']
collection = db['collection']

@app.route('/autocomplete/', methods=['GET'])
def autocomplete():
    value = request.args.get('value')
    ids = []
    latest = []
    results = db.command('text', 'collection', 
                         search=value, 
                         score={'$meta': "textScore" },
                         sort={'score': {'$meta': "textScore"}})['results']
    for result in results:
        if result['obj']['id'] not in ids:
            latest.append({'description':result['obj']['description'],
                           'id': result['obj']['id']})
            ids.append(result['obj']['id'])
    return dumps(latest)


@app.route('/get-food/<int:food_id>', methods=['GET'])
def get_food(food_id):
    value = request.args.get('id')
    result = collection.find_one({"id":food_id}) 
    return dumps(result)

@app.route('/record/', methods=['POST'])
def record_food():
    data = {'food': request.form.get('food_id'),
            'amount': request.form.get('amount'),
            'time': datetime.now()}
    collection = db['records']
    collection.insert(data)
    return dumps({'message': 'ok'})

@app.route('/calculate-day/', methods=['GET'])
def calculate_day():
    collection = db['records']
    yesterday = datetime.now() - timedelta(days = 1)
    results = collection.find({"time": {"$gt": yesterday}})
    for i in results:
        print i

if __name__ == '__main__':
    app.debug = True
    app.run()
