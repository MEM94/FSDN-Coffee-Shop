import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES

## GET Drink Endpoint
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
        
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks],
    })

## GET Drink Details Endpoint
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    drinks = Drink.query.all()
        
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks],
    })


'''
@TODO implement endpoint
    POST /drinks
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
## POST Drink Endpoint
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink():

    data = request.get_json()

    try:
        new_drink = Drink(
            title=data.get('title'),
            recipe = data.get('recipe')
        )

        new_drink.insert()

    except:
        abort(422)
        
    return jsonify({
        'success': True,
        'drinks': '',
    })

    # if request.data:
    #     body = request.get_json()
    #     title = body.get('title', None)
    #     recipe = body.get('recipe', None)
    #     drink = Drink(title=title, recipe=json.dumps(recipe))
    #     Drink.insert(drink)

    #     new_drink = Drink.query.filter_by(id=drink.id).first()

    #     return jsonify({
    #         'success': True,
    #         # 'drinks': [new_drink.long()]
    #     })
    # else:
        # abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
## PATCH Drink Endpoint
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']

    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


## Delete Drink Endpoint
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):

    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    else:
        drink.delete()

    return jsonify({
        'success': True,
        'deleted': drink.id
    })

## Error Handling
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                "success": False, 
                "error": 401,
                "message": "unauthorized"
            }), 401

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                "success": False, 
                "error": 422,
                "message": "unprocessable"
            }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"
        }), 400

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                "success": False, 
                "error": 404,
                "message": "resource not found"
            }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
                "success": False, 
                "error": 500,
                "message": "server_error"
            }), 500

@app.errorhandler(AuthError)
def process_AuthError(error):
    res = jsonify(error.error)
    res.status_code = error.status_code

    return res