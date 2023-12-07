import datetime
import os
import random

import typer

from config import *
from deck import *
from game_view import GameView
from player import Player


class Game:
    def __init__(self, game_view):
        self.game_view = game_view
        self.reset()

    def reset(self):
        self.deck = Deck(self.game_view)
        self.players = []
        self.player_vars = {}
        self.game_vars = {}
        self.current_player_index = 0
        self.current_player = None
        self.game_round = 1
        self.starting_coins = 2
        self.max_players = 5
        self.load_environment_vars()

    def update_game_vars(self):
        try:
            self.starting_coins = int(
                self.game_vars.get("starting_coins", self.starting_coins)
            )
            self.max_players = int(self.game_vars.get("max_players", self.max_players))
        except ValueError:
            if DEBUG:
                self.game_view.display_message(
                    "[DEBUG] Invalid value for game variables. Using default values."
                )

    def load_vars_from_env(self, prefix, target_dict):
        for key, value in os.environ.items():
            if key.startswith(prefix):
                variable_name = key[len(prefix):].lower()

                if value.lower() in ["true", "1"]:
                    target_dict[variable_name] = True
                elif value.lower() in ["false", "0"]:
                    target_dict[variable_name] = False
                else:
                    target_dict[variable_name] = value

        if DEBUG:
            self.game_view.display_message(
                f"[DEBUG] Loaded {prefix} .env vars {target_dict}"
            )

    def load_environment_vars(self):
        self.load_vars_from_env("PLAYER_", self.player_vars)
        self.load_vars_from_env("GAME_", self.game_vars)
        self.update_game_vars()

    def ask(self, question, player_var):
        self.game_view.cli_spacing()
        if question:
            self.game_view.display_message(question)
        return typer.prompt("")

    def set_player_var(self, player_var, question):
        if player_var in self.player_vars:
            return self.player_vars[player_var]
        else:
            if question:
                self.player_vars[player_var] = self.ask(question, player_var)
            else:
                self.player_vars[player_var] = self.ask(
                    f"[yellow]What is the {player_var}?[/yellow]", player_var
                )
            return self.player_vars[player_var]

    def set_game_var(self, game_var, question):
        if game_var in self.game_vars:
            return self.game_vars[game_var]
        else:
            if question:
                self.game_vars[game_var] = self.ask(question, game_var)
            else:
                self.game_vars[game_var] = self.ask(
                    f"[yellow]What is the {game_var}?[/yellow]", game_var
                )
            return self.game_vars[game_var]

    def setup_player(self, player_name, player_type):
        player = Player(
            self, player_name, player_type, self.starting_coins, [], self.game_view
        )
        return player

    def list_players(self):
        self.game_view.display_players()

    def choose_player_count(self):
        players_wanted = self.player_vars.get("players_wanted", None)
        player_bot_name_start_index = 2

        if self.player_vars.get("type", "human") == "bot":
            player_bot_name_start_index = 1

        if self.player_vars.get("type", "human") == "human":
            players_wanted = self.set_player_var(
                player_var="players_wanted",
                question=f"[yellow]How many sneaky players shall you take on? (1 - {self.max_players})[/yellow]",
            )
            if int(players_wanted) < 1 or int(players_wanted) > self.max_players:
                self.game_view.display_message(
                    f"Please choose a number between 1 and {self.max_players}"
                )
                self.choose_player_count()
                return

        self.game_view.display_message(f"Players wanted {players_wanted}")
        for i in range(int(players_wanted)):
            self.players.append(
                self.setup_player(f"Player {player_bot_name_start_index}", "bot")
            )
            player_bot_name_start_index += 1

    def choose_player_name(self):
        player_name = self.set_player_var(
            player_var="name", question="What's your name?"
        )

        if self.player_vars.get("type", "human") == "human":
            self.players.append(self.setup_player(player_name, player_type="human"))

        self.game_view.display_message(f"Welcome to Coup {player_name}!")
        self.game_view.cli_spacing()

    def game_over(self):
        if DEBUG:
            self.game_view.display_message("[DEBUG][GAME] game_over check started")
        if self.game_round > 1000:
            self.game_view.display_message(
                "[DEBUG][GAME]:end: Game over: Too many rounds"
            )
            return True

        playing_players = [
            player for player in self.players if player.state != PlayerState.OUT
        ]
        if len(playing_players) == 1:
            self.game_view.display_empty_line(2)
            self.game_view.display_message("Round " + str(self.game_round))
            self.game_view.display_message("Game Over")
            self.game_view.display_message(
                f":trophy: {playing_players[0].name} wins! :trophy:"
            )
            self.game_view.cli_spacing()
            self.decide_play_again()

            return True

        if len(self.deck.cards) == 0:
            self.game_view.display_empty_line(2)
            self.game_view.display_message(
                "[DEBUG][GAME]:end: Game over: No cards left in the deck"
            )
            return True

        if len(self.players) == 0:
            self.game_view.display_empty_line(2)
            self.game_view.display_message(
                "[DEBUG][GAME]:end: Game over: No players left"
            )
            return True

        if DEBUG:
            self.game_view.display_message("[DEBUG][GAME] game_over check ended")
        return False

    def is_all_bots(self):
        for player in self.players:
            if player.type == "human":
                return False
        return True

    def decide_play_again(self):
        global GAME_COUNT

        if DEBUG:
            self.game_view.display_message(f"[DEBUG][GAME] decide_play_again started")

        self.game_view.display_empty_line(2)
        self.game_view.display_message(
            f"[yellow]Would you like to play again? (y/n)[/yellow]"
        )

        if self.is_all_bots():
            if not GAME_COUNT:
                GAME_COUNT = 1

            GAME_COUNT = int(GAME_COUNT) - 1
            self.game_view.display_message(
                f"GAMES_LEFT: {GAME_COUNT}"
            )
            if GAME_COUNT > 0:
                self.start_game()
                return True
            else:
                self.game_view.display_message(
                    f"ALL GAMES PLAYED"
                )
                return False

        choice = typer.prompt("")

        if choice == "y":
            self.start_game()
            return True
        elif choice == "n":
            return False
        else:
            self.game_view.display_message(f"Invalid choice")
            self.decide_play_again()
            return

    def start_game(self):
        self.reset()

        if DEBUG:
            self.game_view.display_message("")
            self.game_view.display_message(
                "###############################################"
            )
            self.game_view.display_message(f"[DEBUG][NOW] {datetime.datetime.now()}")
            self.game_view.display_message(f"[DEBUG][GAME] START")
        if DEBUG:
            self.game_view.cli_spacing()

        self.choose_player_name()
        self.choose_player_count()

        self.deck.create_deck()
        self.first_deal()

        while not self.game_over():
            self.do_round()
            self.game_round += 1

    def first_deal(self):
        if DEBUG:
            self.game_view.display_message("[DEBUG][GAME] first_deal started")

        if len(self.deck.cards) < 2 * len(self.players):
            self.game_view.display_message(
                "[DEBUG][GAME] Not enough cards in the deck to deal."
            )
            return

        for player in self.players:
            player.cards.extend(self.deck.cards[:2])
            del self.deck.cards[:2]

            if DEBUG:
                self.game_view.display_message("")
                self.game_view.display_message(
                    f"[DEBUG] {player.name}'s hand: {player.get_card_names()}"
                )
        if DEBUG:
            self.game_view.display_message("")
            self.deck.deck_remainder()

    def do_round(self):
        if DEBUG:
            self.game_view.display_message(f"[DEBUG][NOW] {datetime.datetime.now()}")
            self.game_view.display_message(f"[DEBUG][GAME] ROUND {self.game_round}")

        self.current_player_index = 0
        for player in self.players:
            self.do_turn()
            self.current_player_index += 1

    def do_turn(self):
        self.current_player = self.players[self.current_player_index]

        if DEBUG:
            self.game_view.cli_spacing()
            self.game_view.display_message("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            self.game_view.display_message("Player Turn")
            self.game_view.display_message(f"[DEBUG][NOW] {datetime.datetime.now()}")
            self.game_view.display_message(
                f"[DEBUG][GAME] Player Index {self.current_player_index}"
            )
            self.game_view.display_message(
                f"[DEBUG][GAME] Player {self.current_player.name}'s turn"
            )

            self.game_view.display_message("[DEBUG] do_turn started")

        self.current_player.turn_start()
