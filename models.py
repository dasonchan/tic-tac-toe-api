import httplib
import endpoints
import datetime
from protorpc import messages
from google.appengine.ext import ndb


class Player(ndb.Model):
    """Define the Player kind"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    ties = ndb.IntegerProperty(default=0)
    gamesCompleted = ndb.StringProperty(required=True)

    @property
    def _copyPlayerToForm(self):
        pf = PlayerForm()
        for field in pf.all_field():
            if hasattr(self, field.name):
                setattr(pf, field.name, getattr(self, field.name))
        pf.check_initialized()
        return pf

    @property
    def _winningPercentage(self):
        if self.gamesCompleted > 0:
            return float(self.wins)/float(self.gamesCompleted)
        else:
            return 0
    @property
    def _points(self):
        return self.wins * 3 + self.ties

    @classmethod
    def get_player_by_name(cls, name):
        return Player.query(Player.name == name).get()

    def update_stats(self):
        """Adds game to user and update."""
        self.gamesCompleted += 1
        self.put()

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.update_stats()

    def add_tie(self):
        """Add a tie"""
        self.ties += 1
        self.update_stats()

    def add_loss(self):
        """Add a loss. Used as additional method for extensibility."""
        self.update_stats()


class Game(ndb.Model):
    """Define the Game kind"""
    playerOne = ndb.StringProperty(required=True, kind='Player')
    playerTwo = ndb.StringProperty(required=True, kind='Player')
    board = ndb.PickleProperty(required=True)
    currentMove = ndb.IntegerProperty(default=0)
    nextMove = ndb.KeyProperty(required=True)
    gameOver = ndb.BooleanProperty(default=False)
    winner = ndb.KeyProperty()
    tie = ndb.BooleanProperty(default=False)

    @property
    def _copyGameToForm(self):
        gf = GameForm()
        for field in gf.all_field():
            if hasattr(self, field.name):
                setattr(gf, field.name, getattr(self, field.name))
            elif field.name == 'urlsafe_key':
                setattr(gf, field.name, self.key.urlsafe())
            elif field.name == 'board':
                setattr(gf, field.name, str(self.board))
        if winner:
            winner.get().add_win()
            loser = playerOne if winner == self.playerTwo else self.playerTwo
            loser.get().add_loss()
        else:
            self.playerOne.get().add_tie
            self.playerTwo.get().add_tie
        gf.check_initialized()
        return gf

    @property
    def _newGame(self, playerOne, playerTwo):
        game = Game(playerOne = playerOne,
                    playerTwo = playerTwo,
                    nextMove = playerOne)
        game.board = ['' for _ in range(9)]
        game.put()
        return game

class Score(ndb.Model):
    """Define the Score Kind"""
    date = ndb.DateProperty(required=True)
    playerOne = ndb.KeyProperty(required=True)
    playerTwo = ndb.KeyProperty(required=True)
    result = ndb.StringProperty(required=True)

    def _copyScoreToForm(self):
        return ScoreForm(date=str(self.date),
                        playerOne=self.playerOne.get().name,
                        playerTwo=self.playerTwo.get().name,
                        result=self.result)

class PlayerForm(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)
    wins = ndb.IntegerField(3, required=True)
    ties = ndb.IntegerField(4, required=True)
    gamesCompleted = ndb.StringField(5, required=True)
    winningPercentage = ndb.FloatField(6, required=True)
    points = messages.IntegerField(7)

class PlayerForms(messages.Message):
    items = messages.MessageField(PlayerForm, 1, repeated = True)

class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    playerOne = messages.StringField(2)
    playerTwo = messages.StringField(3)
    board = messages.StringField(4)
    nextMove = messages.StringField(5)
    gameOver = messages.BooleanField(6)
    winner = messages.StringField(7)
    tie = messages.BooleanField(8)

class GameForms(messages.Message):
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    playerOne = messages.StringField(1, required=True)
    playerTwo = messages.StringField(2, required=True)

class ScoreForm(messages.Message):
    date = messages.StringField(1, required=True)
    playerOne = messages.StringField(2, required=True)
    playerTwo = messages.StringField(3, required=True)
    result = messages.StringField(4)

class ScoreForms(messages.Message):
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class MoveForm(messages.Message):
    """Used to make a move in an existing game"""
    name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)
