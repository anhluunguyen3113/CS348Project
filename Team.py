# Team.py
from mongoengine import Document, StringField, IntField, ReferenceField


class Team:
    def __init__(self, name, country, trophies, _id=None):
        self._id = _id
        self.name = name
        self.country = country
        self.trophies = trophies
