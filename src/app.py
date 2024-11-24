"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Planet_favorites, People_favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#endpoints:

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
   # print(people[0].serialize)
    print(people[0].planet_id_relationship.serialize()) #trae la info del planeta
    people_serialized = people[0].serialize()
    people_serialized['planet_info'] = people[0].planet_id_relationship.serialize()
    return jsonify({'msg': 'ok',
                    'data': people_serialized})

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404
    person_serialized = person.serialize()
    person_serialized['planet_info'] = person.planet_id_relationship.serialize()
    return jsonify({'msg': 'ok', 'data': person_serialized}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify({'msg': 'ok', 'data': planets_serialized}), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404
    return jsonify({'msg': 'ok', 'data': planet.serialize()}), 200

#parte usuarios y fav:
@app.route('/users', methods={'GET'})
def get_all_users():
    users = User.query.all()
    print(users) #users es una lista con todos los usuarios
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    #serializar es convertir un data tipo modelo a dict
    #solo así se puede convertir en JSON
    return jsonify({'msg': 'ok', 'data': users_serialized}), 200

@app.route('/favorite_planets/<int:user_id>', methods=['GET'])
def get_favorites_by_user(user_id): #lista todos los fav del usuario
    user = User.query.get(user_id)
    print(user)
    print(user.planet_favorites)
    favorite_planets_serialized = []
    for fav_planet in user.planet_favorites:
        favorite_planets_serialized.append(fav_planet.planet_relationship.serialize())
    data = {
        'user_info': user.serialize(),
        'favorite_planets': favorite_planets_serialized
    }
    return jsonify({'msg': 'ok', 'data': data})

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_to_favorites(planet_id): #añade un planeta fav al usuario
    user = User.query.get(1) #qué id?
    planet = Planet.query.get(planet_id)
    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    if planet is None:
        return jsonify({'msg': 'Planeta no encontrado'}), 404

    favorite = Planet_favorites.query.filter_by(user_id=user.id, planet_id=planet.id).first() #para ver si ya lo tiene en favoritos:
    if favorite:
        return jsonify({'msg': 'Este planeta ya está en tus favoritos'}), 400

    new_favorite = Planet_favorites(user_id=user.id, planet_id=planet.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Planeta añadido a favoritos', 'data': new_favorite.serialize()}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_to_favorites(people_id): #añade un personaje fav al usuario
	user = User.query.get(1) #qué id?
	people = People.query.get(people_id)
	if user is None:
		return jsonify({'msg': 'Usuario no encontrado'}), 404
	if people is None:
		return jsonify({'msg': 'Personaje no encontrado'}), 404
	
	favorite = People_favorites.query.filter_by(user_id=user.id, people_id = people.id).first()
	if favorite:
		return jsonify({'msg': 'Este personaje ya está en tus favoritos'}), 400
		
	new_favorite = People_favorites(user_id=user.id, people_id=people.id)
	db.session.add(new_favorite)
	db.session.commit()
	return jsonify({'msg': 'Personaje añadido a favoritos', 'data': new_favorite.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_from_favorites(planet_id):
    user = User.query.get(1)  #qué id?
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    if planet is None:
        return jsonify({'msg': 'Planeta no encontrado'}), 404

    favorite = Planet_favorites.query.filter_by(user_id=user.id, planet_id=planet.id).first()

    if not favorite:
        return jsonify({'msg': 'Este planeta no está en favoritos'}), 400

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'msg': 'Planeta eliminado de favoritos', 'data': favorite.serialize()}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_from_favorites(people_id):
    user = User.query.get(1)  #qué id?
    people = People.query.get(people_id)

    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    if people is None:
        return jsonify({'msg': 'Personaje no encontrado'}), 404

    favorite = People_favorites.query.filter_by(user_id=user.id, people_id=people.id).first()

    if not favorite:
        return jsonify({'msg': 'Este personaje no está en favoritos'}), 400

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'msg': 'Personaje eliminado de favoritos', 'data': favorite.serialize()}), 200

#EXTRAS:
@app.route('/planet', methods=['POST'])
def post_planet():
    #para crear un planeta se necesita un body que contenga nombre y clima del planet
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'El campo name es obligatiorio'}), 400
    if 'climate' not in body:
        return jsonify({'msg': 'El campo climate es obligatorio'}), 400
    new_planet = Planet()
    new_planet.name = body['name']
    new_planet.climate = body['climate']
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({'msg': 'Planeta agregado con éxito', 'data': new_planet.serialized()}), 201

@app.route('/people', methods=['POST'])
def post_people():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'El campo name es obligatorio'}), 400
    if 'gender' not in body:
        return jsonify({'msg': 'El campo gender es obligatorio'}), 400

    planet = Planet.query.get(body['planet_id'])
    if planet is None:
        return jsonify({'msg': 'Planeta no encontrado'}), 400
    new_people = People()
    new_people.name = body['name']
    new_people.gender = body['gender']
    new_people.planet_id = planet.id
    db.session.add(new_people)
    db.session.commit()
    return jsonify({'msg': 'Planeta agregado con éxito', 'data': new_people.serialize()}), 201

@app.route('/planet/<int:id>', methods=['PUT'])
def put_planet(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body or 'climate' not in body:
        return jsonify({'msg': 'Los campos name y climate son obligatorios'}), 400

    planet = Planet.query.get(id)
    if not planet:
        return jsonify({'msg': 'Planeta no encontrado'}), 404

    planet.name = body['name']
    planet.climate = body['climate']
    db.session.commit()
    return jsonify({'msg': 'Planeta actualizado con éxito', 'data': planet.serialize()}), 200

@app.route('/people/<int:id>', methods=['PUT'])
def put_people(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body or 'gender' not in body or 'planet_id' not in body:
        return jsonify({'msg': 'Los campos name, gender y planet_id son obligatorios'}), 400

    person = People.query.get(id)
    if not person:
        return jsonify({'msg': 'Personaje no encontrado'}), 404

    planet = Planet.query.get(body['planet_id'])
    if not planet:
        return jsonify({'msg': 'Planeta no encontrado'}), 400

    person.name = body['name']
    person.gender = body['gender']
    person.planet_id = body['planet_id']
    db.session.commit()
    return jsonify({'msg': 'Personaje actualizado con éxito', 'data': person.serialize()}), 200

@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({'msg': 'Planeta no encontrado'}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': 'Planeta eliminado con éxito'}), 200

@app.route('/people/<int:id>', methods=['DELETE'])
def delete_people(id):
    person = People.query.get(id)
    if not person:
        return jsonify({'msg': 'Personaje no encontrado'}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({'msg': 'Personaje eliminado con éxito'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
