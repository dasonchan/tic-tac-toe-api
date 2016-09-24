from settings import WEB_CLIENT_ID
import endpoints
from protorpc import messages, message_types, remote
from models import PlayerForm, Player, ConflictException
from models import Game, GameForm, GamesForm
from models import Move, MovesForm
from google.appengine.ext import ndb
from datetime import datetime, timedelta
from google.appengine.api import mail
from google.appengine.api import app_identity

