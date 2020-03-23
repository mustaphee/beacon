from flask_pymongo import PyMongo
from bson import json_util, ObjectId
import json

from flask import jsonify, request, current_app as app
from ...routes import api_v2 as api

mongo = PyMongo(app, connect=True)
# mongo = PyMongo()


print(mongo.db)

@api.route('/volunteers')
def get_volunteers():
    try:
        res = mongo.db.volunteers.find()
        data = list(res)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(data))})
    except Exception as er:
        print(er)
        return jsonify({'status': 'fail', 'message': 'AN error occured'})
    
@api.route('/volunteers', methods=['POST'])
def add_volunteers():
    try:
        data = request.get_json()
        r = mongo.db.volunteers.find_one({ 'email': data['email'] })
        if r:
            e = data['email']
            return jsonify({'status': 'fail', 'message': f'Volunteer with email {e} already exist' })
        res = mongo.db.volunteers.insert_one(data)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(res.inserted_id))})
    except Exception as e:
        print(e)
        return jsonify({'status': 'fail', 'message': 'An error occured' })

    

@api.route('/volunteers/<id>', methods=['PUT'])
def update_volunteers(id):
    try:
        res = mongo.db.volunteers.update_one({'_id': ObjectId(id)}, {'$set': request.get_json()})
        return jsonify({ 'status': 'success', 'data': str(res.modified_count)+ ' updated successfully' })
    except Exception as i:
        print(i)
        return jsonify({'status': 'fail', 'message': 'An error occured' })

    
@api.route('/volunteers/<id>', methods=['DELETE'])
def delete_volunteers(id):
    try:
        res = mongo.db.volunteers.delete_one({'_id': ObjectId(id) })
        return jsonify({ 'status': 'success', 'data': str(res.deleted_count)+ ' deleted successfully' })
    except Exception as identifier:
        print(identifier)
        return jsonify({'status': 'fail', 'message': 'An error occured' }) 
    