import httplib
import endpoints
import datetime
from protorpc import messages
from google.appengine.ext import ndb


class Player(ndb.Model):
    """Define the Player kind"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    gamesInProgress = ndb.StringProperty(required=True)
    gamesCompleted = ndb.StringProperty(required=True)

    @property
    def _copyPlayerToForm(self):
        pf = PlayerForm()
        for field in pf.all_field():
            if hasattr(self, field.name):
                setattr(pf, field.name, getattr(self, field.name))
        pf.check_initialized()
        return pf

class Game(ndb.Model):
    """Define the Game kind"""
    name = ndb.StringProperty(required=True)
    spots = ndb.IntegerProperty(default=2)
    playerOne = ndb.StringProperty(required=True, kind='Player')
    playerTwo = ndb.StringProperty(required=True, kind='Player')
    board = ndb.PickProperty(required=True)
    currentMove = ndb.IntegerProperty(default=0)
    nextMove = ndb.StringProperty()
    gameOver = ndb.BooleanProperty(default=False)
    winner = ndb.StringProperty()

    @property
    def _copyGameToForm(self):
        gf = GameForm()
        for field in gf.all_field():
            if hasattr(self, field.name):
                setattr(gf, field.name, getattr(self, field.name))
        gf.check_initialized()
        return gf


class PlayerForm(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)
    gamesInProgress = ndb.StringField(3, required=True)
    gamesCompleted = ndb.StringField(4, required=True)

class PlayerMiniForm(messages.Message):
    name = messages.StringField(1)

class GameForm(messages.Message):
    name = messages.StringField(1)
    spots = messages.IntegerField(2)
    playerOne = messages.StringField(3)
    playerTwo = messages.StringField(4)
    board = messages.StringField(5)
    currentMove = messages.IntegerField(6)
    gameOver = messages.BooleanField(7)
    winner = messages.StringField(8)