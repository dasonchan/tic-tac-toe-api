import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import TicTacToeApi
from utils import get_by_urlsafe

from models import Player, Game


class MainHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write('Hello world!')


class SendReminderEmail(webapp2.RequestHandler):

    def get(self):
        """Send a reminder email to player who currently has games
        in progress"""
        players = Player.query(Player.email != None)

        for player in players:
            games = Game.query(ndb.OR(Game.playerOne == player.key,
                                      Game.playerTwo == player.key)).filter(Game.gameOver == False)
            if games.count() > 0:
                subject = 'Tic Tac Toe Reminder'
                body = 'Hello {}, you have {} games in progress. Their' \
                       ' keys are: {}'.format(player.name,
                                              games.count(),
                                              ', '.join(game.key.urlsafe() for game in games))
                logging.debug(body)

                mail.send_mail('noreply@{}.appspotmail.com'.format(app_identity.get_application_id()),
                               player.email,
                               subject,
                               body)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
