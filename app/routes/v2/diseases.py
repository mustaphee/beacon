from flask_pymongo import PyMongo
from bson import json_util, ObjectId
import json
import requests
from datetime import datetime as dt
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError

from flask import jsonify, request, current_app as app
from ...routes import api_v2 as api

from cachetools import cached, TTLCache

mongo = PyMongo(app, connect=True)
# mongo = PyMongo()

class LatestModel(BaseModel):
    confirmed: int
    recovered: int
    deaths: int

class LocationModel(BaseModel):
    country_name: str
    country_code: str = ''
    last_updated: str = str(dt.now())
    province: str = ''
    yesterday: Dict = {}
    latest: LatestModel

class DiseaseModel(BaseModel):
    name: str
    description: str
    first_occurence_date: str
    first_reported_at: str = 'Unknown'
    latest: LatestModel = {}
    locations: List[LocationModel] = []


@api.route('/all-epidemics')
def get_epidemic():
    try:
        res = mongo.db.epidemic.find()
        data = list(res)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(data))})
    except Exception as er:
        print(er)
        return jsonify({'status': 'fail', 'message': 'AN error occured'})
    
@api.route('/epidemic', methods=['POST'])
def add_epidemic():
    try:
        data = request.get_json()
        r = mongo.db.epidemic.find_one({ 'name': data['name'] })
        if r:
            e = data['name']
            return jsonify({'status': 'fail', 'message': f'Disease with name {e} already exist' })
        print(data)
        disease = DiseaseModel(**data)
        # disease = DiseaseModel(name=data['name'], description=data['description'], 
        # first_occurence_date=data['first_occurence_date'], first_reported_at=data['first_reported_at'])
        res = mongo.db.epidemic.insert_one(disease.dict())
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(res.inserted_id))})

    except ValidationError as ve:
        print(ve)
        return jsonify({'status': 'fail', 'message': 'An error occured', 'error': ve.errors() })

    except Exception as e:
        print(type(e))
        return jsonify({'status': 'fail', 'message': 'An error occured' })


def is_existing(locations, country_name):
    for i, location in enumerate(locations):
        if location['country_name'].lower() == country_name.lower():
            return str(i)
    return False
    

@api.route('/epidemic/<id>', methods=['PUT'])
def update_epidemic(id):
    try:
        data = request.get_json()
        data = dict(data)
        epid = mongo.db.epidemic.find_one({'_id': ObjectId(id) })
        dictedEpid = dict(epid)
        
        newLocation = LocationModel(**data)
        i = is_existing(dictedEpid['locations'], data['country_name'])
        if i:
            dictedEpid['locations'][int(i)] = data
        else:
            dictedEpid['locations'].append(data)
        # dictedEpid['locations'].append(data)
        # if len(dictedEpid['locations']) > 1:
        #     for i, location in enumerate(dictedEpid['locations']):
        #         if location['country_name'].lower() == data['country_name'].lower():
        #             dictedEpid['locations'].pop()
        #             dictedEpid['locations'][i] == data
        #             break
        totalConfirmed, totalDeaths, totalRecovered = 0, 0, 0
        for latest in dictedEpid['locations']:
            print(latest)
            if latest:
                totalConfirmed = totalConfirmed + latest['latest']['confirmed']
                totalDeaths = totalDeaths + latest['latest']['deaths']
                totalRecovered = totalRecovered + latest['latest']['recovered']
        totalLatest = {'confirmed': totalConfirmed, 'deaths': totalDeaths, 'recovered': totalRecovered }
        dictedEpid['latest'] = totalLatest
        print(dictedEpid)

        # return jsonify({'status': 'OK'})
        res = mongo.db.epidemic.update_one({'_id': ObjectId(id)}, {'$set': dictedEpid})

        return jsonify({ 'status': 'success', 'data': str(res.modified_count)+ ' updated successfully' })

    except ValidationError as ve:
        print(ve)
        print(type(ve))
        return jsonify({'status': 'fail', 'message': 'An error occured', 'error': ve.errors() })

    except Exception as i:
        print(i)
        print(type(i))
        return jsonify({'status': 'fail', 'message': 'An error occured' })

    
@api.route('/epidemic/<id>', methods=['GET'])
def get_an_epidemic(id):
    try:
        res = mongo.db.epidemic.find_one({'_id': ObjectId(id) })
        data = dict(res)
        return jsonify({'status': 'success', 'data': json.loads(json_util.dumps(data))})
    except Exception as identifier:
        print(identifier)
        return jsonify({'status': 'fail', 'message': 'An error occured' }) 

@api.route('/epidemic/<id>', methods=['DELETE'])
def delete_epidemic(id):
    try:
        res = mongo.db.epidemic.delete_one({'_id': ObjectId(id) })
        return jsonify({ 'status': 'success', 'data': str(res.deleted_count)+ ' deleted successfully' })
    except Exception as identifier:
        print(identifier)
        return jsonify({'status': 'fail', 'message': 'An error occured' }) 

