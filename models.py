from flask import Flask
from flask_mongoengine import MongoEngine
from mongoengine import Document, StringField, IntField, ReferenceField

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'soccer_db',
    'host': 'mongodb://localhost/soccer_db'
}

db = MongoEngine(app)
class Team(Document):
    name = StringField(required=True)
    country = StringField(required=True)
    trophies = IntField(default=0)

class Player(Document):
    name = StringField(required=True)
    position = StringField(required=True)
    age = IntField(required=True)
    trophies = IntField(default=0)
    ballondor = IntField(default=0)
    team = ReferenceField(Team)
