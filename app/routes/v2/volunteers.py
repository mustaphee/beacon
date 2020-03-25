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

@cached(cache=TTLCache(maxsize=1024, ttl=600))
@api.route('/get-news-headlines')
def get_news_headlines():
    r = request.args.get('country', '')
    if r.lower() == 'ng':
        url = BASE_URL.format('&country=ng')
    else:
        url = BASE_URL.format('')
    res = requests.get(url)
    data = json.loads(res.content)
    return jsonify(data)

@api.route('/update-ng-data', methods = ['PUT'])    
def update_ng():
    data = request.get_json()
    

    try:
        if not data['deaths'] and not data['recovered'] and not data['confirmed']:
            pass
        r = mongo.db.nigeria.find_one({ 'country_name': 'Nigeria' })
        latest = {
            "confirmed": data['confirmed'],
            "deaths": data['deaths'],
            "recovered": data['recovered'],
        }
        if dt.now().day > int(r['locations'][0]['last_updated'][8:10]):
            yesterday =  {
                "confirmed": r['latest']['confirmed'],
                "deaths": r['latest']['deaths'],
                "recovered": r['latest']['recovered']
            }
            r['locations'][0]['yesterday'] = yesterday

        r['locations'][0]['last_updated'] = str(dt.now()) + 'Z'
        r['latest'] = latest
        r['locations'][0]['latest'] = latest
        
        # print(r)'%m/%d/%y %H:%M:%S'
        # return 'ok'
        res = mongo.db.nigeria.update_one({'country_name': 'Nigeria'}, {'$set': r})
        return jsonify({ 'status': 'success', 'data': str(res.modified_count)+ ' updated successfully' })
    except KeyError as ke:
        print(ke)
        return jsonify({'status': 'fail', 'message': f'You did not supply the necessary data for {ke}' })

    except Exception as i:
        print(i)
        return jsonify({'status': 'fail', 'message': 'An error occured' })
