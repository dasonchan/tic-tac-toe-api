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
    gamesCompleted = ndb.IntegerProperty(default=0)

    @property
    def copyPlayerToForm(self):
        pf = PlayerForm()
        for field in pf.all_fields():
            if hasattr(self, field.name):
                setattr(pf, field.name, getattr(self, field.name))
        pf.check_initialized()
        return pf

    @property
    def winningPercentage(self):
        if self.gamesCompleted > 0:
            return float(self.wins)/float(self.gamesCompleted)
        else:
            return float(0)
    @property
    def points(self):
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
    playerOne = ndb.KeyProperty(required=True)
    playerTwo = ndb.KeyProperty(required=True)
    board = ndb.PickleProperty(required=True)
    nextMove = ndb.KeyProperty(required=True)
    gameOver = ndb.BooleanProperty(default=False)
    winner = ndb.KeyProperty()
    tie = ndb.BooleanProperty(default=False)
    history = ndb.PickleProperty(required=True)

    def copyGameToForm(self):
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        board=str(self.board),
                        playerOne=self.playerOne.get().name,
                        playerTwo=self.playerTwo.get().name,
                        nextMove=self.nextMove.get().name,
                        gameOver=self.gameOver,
                        )
        if self.winner:
            form.winner = self.winner.get().name
        if self.tie:
            form.time = self.tie
        return form
    
    @classmethod
    def newGame(cls, playerOne, playerTwo):
        board = ['' for _ in range(9)]
        
        game = Game(playerOne = playerOne,
                    playerTwo = playerTwo,
                    nextMove = playerOne,
                    board = board)
        game.history = []

        game.put()
        return game
    
    def endGame(self, winner=None):
        self.gameOver = True
        if winner:
            self.winner = winner
        else:
            self.tie = True
        self.put()
        
        # update results 
        if winner:
            result = 'Player One' if winner == self.playerOne else 'Player Two'
            winner.get().add_win()
            loser = self.playerOne if winner == self.playerTwo else self.playerTwo
            loser.get().add_loss()
        else:
            result = 'tie'
            self.playerOne.get().add_tie()
            self.playerTwo.get().add_tie()
        
        score = Score(date=datetime.datetime.now(),
                      playerOne=self.playerOne,
                      playerTwo=self.playerTwo,
                      result=result)
        score.put()

class Score(ndb.Model):
    """Define the Score Kind"""
    date = ndb.DateProperty(required=True)
    playerOne = ndb.KeyProperty(required=True)
    playerTwo = ndb.KeyProperty(required=True)
    result = ndb.StringProperty(required=True)

    def copyScoreToForm(self):
        return ScoreForm(date=str(self.date),
                        playerOne=self.playerOne.get().name,
                        playerTwo=self.playerTwo.get().name,
                        result=self.result)

class PlayerForm(messages.Message):
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    ties = messages.IntegerField(4, required=True)
    gamesCompleted = messages.IntegerField(5, required=True)
    winningPercentage = messages.FloatField(6, required=True)
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
    message = messages.StringField(1, required=True)
