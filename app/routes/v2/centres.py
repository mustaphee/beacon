from flask_pymongo import PyMongo
from bson import json_util, ObjectId
import json
import requests
from datetime import datetime as dt

from flask import jsonify, request, current_app as app
from ...routes import api_v2 as api

from cachetools import cached, TTLCache

mongo = PyMongo(app, connect=True)
# mongo = PyMongo()
BASE_URL = 'http://newsapi.org/v2/top-headlines?q=coronavirus{}&apiKey=55ae0da6ab2b4fe09157434c11615961'

@api.route('/centres')
def get_centres():
    try:
        res = mongo.db.centres.find()
        data = list(res)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(data))})
    except Exception as er:
        print(er)
        return jsonify({'status': 'fail', 'message': 'AN error occured'})
    
@api.route('/centres', methods=['POST'])
def add_centres():
    try:
        data = request.get_json()
        r = mongo.db.centres.find_one({ 'name': data['name'] })
        if r:
            e = data['name']
            return jsonify({'status': 'fail', 'message': f'Volunteer with email {e} already exist' })
        res = mongo.db.centres.insert_one(data)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(res.inserted_id))})
    except Exception as e:
        print(e)
        return jsonify({'status': 'fail', 'message': 'An error occured' })

    

@api.route('/centres/<id>', methods=['PUT'])
def update_centres(id):
    try:
        res = mongo.db.centres.update_one({'_id': ObjectId(id)}, {'$set': request.get_json()})
        return jsonify({ 'status': 'success', 'data': str(res.modified_count)+ ' updated successfully' })
    except Exception as i:
        print(i)
        return jsonify({'status': 'fail', 'message': 'An error occured' })

    
@api.route('/centres/<id>', methods=['DELETE'])
def delete_centres(id):
    try:
        res = mongo.db.centres.delete_one({'_id': ObjectId(id) })
        return jsonify({ 'status': 'success', 'data': str(res.deleted_count)+ ' deleted successfully' })
    except Exception as identifier:
        print(identifier)
        return jsonify({'status': 'fail', 'message': 'An error occured' }) 
