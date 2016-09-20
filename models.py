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


class PlayerForm(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)
    gamesInProgress = ndb.StringField(3, required=True)
    gamesCompleted = ndb.StringField(4, required=True)

class PlayerMiniForm(messages.Message):
    name = messages.StringField(1)
