#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import TicTacToeApi
from utils import get_by_urlsafe

from models import Player, Game

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class UpdateGamesFinished(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        TicTacToeApi._update_finished_games()
        self.response.set_status(204)

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
    ('/tasks/update_finished_games', UpdateGamesFinished),
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
