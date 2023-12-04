from typing import List

from deck import Deck
from game import Game
from game_view import GameView
from player import Player


class GameController:
    def __init__(self):
        self.game_view = GameView()
        self.game = Game(self.game_view)
        self.game_view.game = self.game

    def start_game(self):
        self.game.start_game()
