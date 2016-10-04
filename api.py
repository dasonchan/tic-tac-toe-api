import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import memcache, mail
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import Player, Game, Score, NewGameForm, StringMessage, GameForm, MoveForm, ScoreForm, ScoreForms, GameForms, PlayerForm, PlayerForms
from utils import get_by_urlsafe, check_winner
from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    playerOne=messages.StringField(1),
    playerTwo=messages.StringField(2)
    )
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MoveForm, urlsafe_game_key=messages.StringField(1),)
PLAYER_REQUEST = endpoints.ResourceContainer(name=messages.StringField(1), email=messages.StringField(2))

# MEMCACHE_GAMES_PLAYED = "GAMES_PLAYED"


@endpoints.api(name='tic_tac_toe',
               version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class TicTacToeApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=PlayerForm,
                      path='player',
                      name='create_player',
                      http_method='POST')
    def create_player(self, request):
        """Check if user name is unique"""
        if Player.get_player_by_name(request.name):
            raise endpoints.ConflictException('The name has been taken!')
        if not mail.is_email_valid(request.email):
            raise endpoints.BadRequestException('Please input a valid email address')
        player = Player(name=request.name, email=request.email)
        player.put()
        return player._copyPlayerToForm
    
    @endpoints.method(response_message=PlayerForms,
                      path='player/ranking',
                      name='get_player_rankings',
                      http_method='GET')
    def get_player_rankings(self, request):
        """Return rankings for all Players"""
        players = Player.query(Player.gamesCompleted > 0).fetch()
        players = sorted(players, key=lambda x :x._points, reverse=True)
        return PlayerForms(items=[player._copyPlayerToForm for player in players])
    
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Start a new game"""
        playerOne = Player.get_player_by_name(request.playerOne)
        playerTwo = Player.get_player_by_name(request.playerTwo)
        # Check if players registered 
        if not playerOne or not playerTwo:
            name = request.playerOne if not playerOne else request.playerTwo
            raise endpoints.NotFoundException('Player %s does not exist' % name)
        game = Game.newGame(playerOne.key, playerTwo.key)
        
        return game._copyGameToForm()



api = endpoints.api_server([TicTacToeApi,])
