import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, mail
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import Player, Game, Score, NewGameForm, StringMessage, GameForm, MoveForm, ScoreForm, ScoreForms, GameForms, PlayerForm, PlayerForms
from utils import get_by_urlsafe, check_winner

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

# NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
# GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
# MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MoveForm, urlsafe_game_key=messages.StringField(1),)
PLAYER_REQUEST = endpoints.ResourceContainer(name=messages.StringField(1), email=messages.StringField(2))

# MEMCACHE_GAMES_PLAYED = "GAMES_PLAYED"

@endpoints.api(name='tic_tac_toe',
               version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class TicTacToeApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=StringMessage,
                      path='player',
                      name='create_player',
                      http_method='POST')
    def create_player(self, request):
        """Check if user name is unique"""
        if Player.get_player_by_name(request.name):
            raise endpoints.ConflictException('The name has been taken!')
        if not mail.is_email.valid(request.email):
            raise endpoints.BadRequestException('Please input a valid email address')
        player = Player(name=request.name, email=request.email)
        player.put()
        return StringMessage(message='Player {} created!'.format(request.name))



api = endpoints.api_server([TicTacToeApi])
