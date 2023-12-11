from mongoengine import Document, StringField, IntField, ReferenceField

class Player:
    def __init__(self, name, position, age, trophies, ballondor, team=None, _id=None):
        self._id = _id
        self.name = name
        self.position = position
        self.age = age
        self.trophies = trophies
        self.ballondor = ballondor
        self.team = team
