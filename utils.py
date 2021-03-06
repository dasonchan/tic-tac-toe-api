"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def check_winner(board):
    return (board[0] == board[1] == board[2] != '' or
            board[3] == board[4] == board[5] != '' or
            board[6] == board[7] == board[8] != '' or
            board[0] == board[3] == board[6] != '' or
            board[1] == board[4] == board[7] != '' or
            board[2] == board[5] == board[8] != '' or
            board[0] == board[4] == board[8] != '' or
            board[2] == board[4] == board[6] != '')


def check_full(board):
    """Return true if the board is full"""
    for block in board:
        if not block:
            return False
    return True
