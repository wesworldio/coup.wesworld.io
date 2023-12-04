import random

from config import *
from game_view import GameView

DECK_CONFIG = [
    {"name": "Ambassador", "total_count": 3},
    {"name": "Assassin", "total_count": 3},
    {"name": "Captain", "total_count": 3},
    {"name": "Contessa", "total_count": 3},
    {"name": "Duke", "total_count": 3},
]


class Deck:
    def __init__(self, game_view):
        self.cards_starting = []
        self.cards = []
        self.discard_pile = []
        self.game_view = game_view

    def deck_remainder(self):
        if DEBUG:
            self.game_view.display_message("[DEBUG][DECK] Remaining deck:")

        for card in self.cards:
            self.game_view.display_message(card["name"])

    def create_deck(self):
        self.cards_starting = []
        for card in DECK_CONFIG:
            total_count = int(card["total_count"])
            for i in range(total_count):
                new_card = {"name": card["name"], "state": CardState.HIDDEN}
                self.cards_starting.append(new_card)

        self.cards = self.cards_starting.copy()
        if DEBUG:
            self.game_view.display_message("[DEBUG][DECK] Starting Deck")
            self.game_view.display_message(self.cards)

        random.shuffle(self.cards)
        if DEBUG:
            self.game_view.display_message("[DEBUG][DECK] Shuffled Deck")
            self.game_view.display_message(self.cards)

    def get_next_card(self):
        if DEBUG:
            self.game_view.display_message("[DEBUG][DECK] get_next_card started")

        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def add_to_discard(self, card):
        self.discard_pile.append(card)

    def reshuffle_discard_into_deck(self):
        random.shuffle(self.discard_pile)
        self.cards.extend(self.discard_pile)
        self.discard_pile.clear()

    @classmethod
    def cards_to_string(cls, cards):
        card_names = [d["name"] for d in cards if "name" in d]
        return style_text(", ".join(card_names))

    @classmethod
    def cards_to_list(cls, cards):
        table = Table("Choice", "Character")
        for i, card in enumerate(cards):
            table.add_row(str(i + 1), style_text(card["name"]))

        return table
