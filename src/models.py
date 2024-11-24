from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    planet_favorites = db.relationship('Planet_favorites', back_populates='user_relationship')
    people_favorites = db.relationship('People_favorites', back_populates='user_relationship')

    def __repr__(self):
        return '<User %r>' % self.email
    
    """ def __repr__(self):
     return f'Usuario {self.email} y id {self.id}' """

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "password": self.password
            # do not serialize the password, its a security breach
        }
    
class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    climate = db.Column(db.String(50), nullable=False)
    residents = db.relationship('People', back_populates='planet_id_relationship')
    favorite_planets = db.relationship('Planet_favorites', back_populates='planet_relationship')

    def __repr__(self):
        return f'Planeta {self.name} con clima {self.climate}'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'climate': self.climate
        }


class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    planet_id_relationship = db.relationship('Planet', back_populates='residents')
    favorite_people = db.relationship('People_favorites', back_populates='people_relationship')


    def __repr__(self):
        return f'{self.name} is a {self.gender} character'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender
        } 
    
class Planet_favorites(db.Model):
    __tablename__ = 'planet_favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates = 'planet_favorites')
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet_relationship = db.relationship('Planet', back_populates='favorite_planets')

    def __repr__(self):
        return f'El usuario {self.user_id} , tiene como favorito al planeta {self.planet_id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'planet_id': self.planet_id
        }

class People_favorites(db.Model):
	__tablename__ = 'people_favorites'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user_relationship = db.relationship('User', back_populates = 'people_favorites')
	people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
	people_relationship = db.relationship('People', back_populates='favorite_people')
	
	def __repr__(self):
		return f'El usuario {self.user_id}, tiene como favorito al personaje {self.people_id}'
	
	def serialize(self):
		return {
			'id': self.id,
			'user_id': self.user_id,
			'people_id': self.people_id
		}