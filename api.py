import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import memcache, mail
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import (
    Player, 
    Game, 
    Score, 
    StringMessage, 
    GameForm, 
    ScoreForm, 
    ScoreForms, 
    GameForms, 
    PlayerForm, 
    PlayerForms)
from utils import get_by_urlsafe, check_winner, check_full
from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    playerOne=messages.StringField(1),
    playerTwo=messages.StringField(2)
    )
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    name=messages.StringField(1, required=True), 
    move=messages.StringField(2, required=True), 
    urlsafe_game_key=messages.StringField(3, required=True),)
PLAYER_REQUEST = endpoints.ResourceContainer(name=messages.StringField(1), email=messages.StringField(2))

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
        """Create a new player"""
        # Check if user name is unique
        if Player.get_player_by_name(request.name):
            raise endpoints.ConflictException('The name has been taken!')
        if not mail.is_email_valid(request.email):
            raise endpoints.BadRequestException('Please input a valid email address')
        player = Player(name=request.name, email=request.email)
        player.put()
        return player.copyPlayerToForm
    
    @endpoints.method(response_message=PlayerForms,
                      path='player/ranking',
                      name='get_player_rankings',
                      http_method='GET')
    def get_player_rankings(self, request):
        """Return rankings for all Players"""
        players = Player.query(Player.gamesCompleted > 0).fetch()
        players = sorted(players, key=lambda x :x.points, reverse=True)
        return PlayerForms(items=[player.copyPlayerToForm for player in players])
    
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
        
        return game.copyGameToForm()
    
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game does not exist!')
        
        return game.copyGameToForm()
    
    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=GameForms,
                      path='player/games',
                      name='get_player_games',
                      http_method='GET')
    def get_player_games(self, request):
        """Return all games from Player"""
        player = Player.get_player_by_name(request.name)
        if not player:
            raise endpoints.NotFoundException('Player does not exist')
        games = Game.query(ndb.OR(Game.playerOne == player.key,
                                  Game.playerTwo == player.key)).filter(Game.gameOver == False)
        
        return GameForms(items=[game.copyGameToForm() for game in games])
    
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}', 
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Delete a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.gameOver:
            game.key.delete()
            return StringMessage(message='Game - {} deleted.'.format(request.urlsafe_game_key))
        elif game and game.gameOver:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')
        
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Make a move. Returns current game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.gameOver:
            raise endpoints.NotFoundException('Game is over')
        
        player = Player.get_player_by_name(request.name)
        # check if player has next move
        if player.key != game.nextMove:
            raise endpoints.BadRequestException('It is not your turn')
        # check if input for move numeric
        if request.move.isnumeric() == False:
            raise endpoints.BadRequestException('Please input a number for move')
        
        move = int(float(request.move))
        # check if input for move within 9
        if move in range(9):        
            if game.board[move] != '':
                raise endpoints.BadRequestException('The block has been filled')
            # x is true when is player one's turn; false when player two's turn
            x = True if player.key == game.playerOne else False
            game.board[move] = 'X' if x else 'O'
            game.history.append(('X' if x else 'O', move))
            game.nextMove = game.playerTwo if x else game.playerOne
            
            # check if there is a winner
            winner = check_winner(game.board)
            if winner:
                game.endGame(player.key)
            else:
                if check_full(game.board):
                    # tie
                    game.endGame()
    
            game.put()

        else:
            raise endpoints.BadRequestException('Input for move can only be 0~8')
        
        
        return game.copyGameToForm()
       
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))
        
    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        player = Player.get_player_by_name(request.name)
        if not player:
            raise endpoints.NotFoundException('Player does not exist')
        scores = Score.query(ndb.OR(Score.playerOne == player.key,
                                    Score.playerTwo == player.key))
        return ScoreForms(items=[score.copyScoreToForm() for score in scores])
    
api = endpoints.api_server([TicTacToeApi,])
