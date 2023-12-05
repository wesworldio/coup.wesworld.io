from config import *
from deck import Deck
from game_view import GameView  # Import the GameView class


class Player:
    def __init__(self, game, name, type, coins, cards, game_view):
        self.game = game
        self.name = name
        self.type = type
        self.coins = coins
        self.cards = cards
        self.chosen_card = None
        self.actions = [
            {
                "name": "Income",
                "fn": self.income,
                "action_string": "take income",
                "description": "Take 1 coin from the treasury",
                "character": "*",  # All
                "can_challenge": False,
                "can_block": False,
                "requirements": [
                    {"key": "sender_player.alive", "value": True},
                    {"key": "sender_player.turn", "value": True},
                ],
                "effects": {
                    "sender_player": [
                        {
                            "coin": 1,
                        },
                    ],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            {
                "name": "Foreign Aid",
                "fn": self.foreign_aid,
                "action_string": "take foreign aid",
                "description": "take 2 coins from the treasury",
                "character": "*",  # All
                "can_challenge": False,
                "can_block": True,
                "requirements": [
                    {"key": "sender_player.alive", "value": True},
                    {"key": "sender_player.turn", "value": True},
                ],
                "effects": {
                    "sender_player": [
                        {
                            "coin": 2,
                        },
                    ],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            {
                "name": "Tax",
                "fn": self.tax,
                "action_string": "take 3 coins",
                "description": "[bold deep_pink3]Take [grey70]3 coins[/grey70] from the treasury[/bold deep_pink3]",
                "character": "Duke",
                "can_challenge": True,
                "can_block": False,
                "requirements": [
                    {"key": "player.alive", "value": True},
                    {"key": "player.turn", "value": True},
                ],
                "effects": {
                    "sender_player": [{"key": "player.coins", "value": 3}],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            {
                "name": "Coup",
                "fn": self.coup,
                "action_string": "coup",
                "description": "Pay 7 coins to launch a coup against an opponent, forcing that player to lose an influence. (If you have 10 or more coins, you must take this action.)",
                "character": "*",  # All
                "can_challenge": False,
                "can_block": False,
                "requirements": [
                    {"key": "sender_player.alive", "value": True},
                    {"key": "sender_player.turn", "value": True},
                    {"key": "sender_player.coins", "value": -7},
                ],
                "effects": {
                    "sender_player": [{"choice": "rec_player"}],
                    "rec_player": [{"rec_player_choice": "rec_card"}],
                    "game": [
                        {
                            "action": "rec_player_choice",
                        },
                    ],
                },
            },
            {
                "name": "Assassinate",
                "fn": self.assassinate,
                "action_string": "[grey30]assassinate[/grey30]",
                "description": "[grey30]Pay [grey70]3 coins[/grey70] to try to [grey30]assassinate[/grey30] another player's character[/grey30]",
                "character": "Assassin",
                "can_challenge": True,
                "can_block": True,
                "requirements": [
                    {"key": "player.alive", "value": True},
                    {"key": "player.turn", "value": True},
                    {"key": "player.coins", "value": -3},
                ],
                "effects": {
                    "sender_player": [
                        {"key": "player.coins", "value": -3},
                    ],
                    "rec_player": [{"key": "card.alive", "value": -1}],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            {
                "name": "Exchange",
                "fn": self.exchange,
                "action_string": "[bold yellow4]exchange cards with the Court Deck[/bold yellow4]",
                "description": "[bold yellow4]Exchange cards with the Court Deck[/bold yellow4]",
                "character": "Ambassador",
                "can_challenge": True,
                "can_block": False,
                "requirements": [
                    {"key": "player.alive", "value": True},
                    {"key": "player.turn", "value": True},
                ],
                "effects": {
                    "sender_player": [{"key": "player.cards", "value": "exchange"}],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            {
                "name": "Steal",
                "fn": self.steal,
                "action_string": "[bold deep_sky_blue1]steal [grey70]2 coins[/grey70] from[/bold deep_sky_blue1]",
                "description": "[bold deep_sky_blue1]take [grey70]2 coins[/grey70] from another player[/bold deep_sky_blue1]",
                "character": "Captain",
                "can_challenge": True,
                "can_block": True,
                "requirements": [
                    {"key": "player.alive", "value": True},
                    {"key": "player.turn", "value": True},
                ],
                "effects": {
                    "sender_player": [{"key": "player.coins", "value": 2}],
                    "rec_player": [{"key": "player.coins", "value": -2}],
                    "game": [
                        {
                            "action": "next_turn",
                        },
                    ],
                },
            },
            # {
            #     "name": "Contessa",
            #     "fn": self.contessa,
            #     "action_string": "block the assassination of",
            #     "description": "[bold red3]Block assassination attempts[/bold red3]",
            #     "character": "Contessa",
            #     "can_challenge": True,
            #     "requirements": [
            #         {
            #             "key": "player.alive",
            #             "value": True
            #         },
            #         {
            #             "key": "player.turn",
            #             "value": False
            #         },
            #     ],
            #     "effects": {
            #         "rec_player": [
            #             {
            #                 "key": "player.cards[0].dying",
            #                 "value": False
            #             }
            #         ],
            #     }
            # }
        ]
        self.chosen_action = None
        self.rec_player = None
        self.state = PlayerState.PLAYING
        self.requirements = None
        self.game_view = game_view  # Store the GameView instance

    def player_cards(self):
        self.game_view.display_player_cards(self)

    def get_card_names(self):
        return self.get_visible_card_names(self)

    def get_visible_card_names(self, player):
        if CHEAT_SEE_ALL_CARDS:
            return Deck.cards_to_string(player.cards)
        return Deck.cards_to_string(
            [card for card in player.cards if card["state"] == CardState.VISIBLE]
        )

    def turn_start(self):
        os.system("clear")
        self.update_players_state()
        self.rec_player = None
        self.sender_player = self.game.players[self.game.current_player_index]

        if self.sender_player.state == PlayerState.OUT:
            return

        self.sender_player.state = PlayerState.TURN

        self.game_view.display_turn_start(self)

        self.choose_action()

        self.turn_validate()

        self.turn_end()

        self.sender_player.state = PlayerState.PLAYING

    def random_action_choice(self):
        choice = random.randint(0, len(self.actions) - 1)
        return self.actions[choice]

    def input_action_choice(self):
        choice = None
        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            self.chosen_action = self.random_action_choice()
        else:
            choice = typer.prompt("")
            if not choice.isdigit() or int(choice) > len(self.actions):
                self.game_view.display_error_message("Invalid choice")
                self.input_action_choice()
                return
            self.chosen_action = self.actions[int(choice) - 1]

        return choice

    def input_action_exchange(self):
        choice = None
        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            choices = random.sample(range(1, 5), 2)
            choice = f"{choices[0]} {choices[1]}"
        else:
            choice = typer.prompt("")
        return choice

    def choose_action(self):
        if self.coins >= 10:
            self.game_view.display_empty_line()
            self.game_view.display_message(
                f"{self.name} has {coins_text(self.coins)} so they must perform a coup"
            )
            for action in self.actions:
                if action["name"] == "Coup":
                    self.chosen_action = action
                    break

        else:
            self.game_view.display_available_actions(self)
            self.input_action_choice()
        try:
            action_fn = self.chosen_action["fn"]
            self.game_view.display_message(
                f"{self.name} chose {style_text(self.chosen_action['name'])}"
            )
            action_fn()
        except KeyError:
            return
        except StopIteration:
            self.game_view.display_error_message("Action not found")
            self.choose_action()

    def turn_validate(self):
        is_valid = True

        if self.chosen_action and self.chosen_action["can_challenge"]:
            challenge_check_result = self.turn_check_challenge()
            if not challenge_check_result:
                return False

        if self.chosen_action and self.chosen_action["can_block"]:
            block_check_result = self.turn_check_block()
            if not block_check_result:
                return False

        return is_valid

    def turn_check_challenge(self):
        is_challenged = False
        sender_player = self
        for player in self.game.players:
            if player.name == sender_player.name:
                continue

            if player.state == PlayerState.PLAYING:
                if player.decide_challenge():
                    challenge_result = player.challenge(sender_player)
                    if challenge_result:
                        return False
                    else:
                        continue

        self.game_view.display_empty_line()
        return True

    def turn_check_block(self):
        is_blocked = False

        sender_player = self
        for player in self.game.players:
            if player.name == sender_player.name:
                continue

            if player.state == PlayerState.PLAYING:
                if player.decide_block():
                    return False

        self.game_view.display_empty_line()
        return True

    def both_cards_visible(self):
        both_cards_visible = True

        for card in self.cards:
            if card["state"] != CardState.VISIBLE:
                both_cards_visible = False
                break
        return both_cards_visible

    def update_players_state(self):
        for player in self.game.players:
            if player.both_cards_visible() and player.state == PlayerState.PLAYING:
                player.state = PlayerState.OUT
                self.game_view.display_empty_line()
                self.game_view.display_message(
                    f":skull::skull::skull::skull::skull::skull::skull::skull::skull::skull:"
                )
                self.game_view.display_message(
                    f":skull: {player.name} is out of the game"
                )
                self.game_view.display_message(
                    f":skull::skull::skull::skull::skull::skull::skull::skull::skull::skull:"
                )
                self.game_view.display_empty_line()

    def turn_end(self):
        if self.rec_player:
            self.game_view.display_message(
                f"{self.name} chose to {style_text(self.chosen_action['action_string'])} {self.rec_player.name}"
            )

    def choose_player(self):
        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            choice = random.randint(0, len(self.game.players) - 1)
            while choice == self.game.current_player_index:
                choice = random.randint(0, len(self.game.players) - 1)
            return self.game.players[choice]

        self.game_view.display_message(
            f"[yellow]Who does {self.name} want to {style_text(self.chosen_action['action_string'])}?[/yellow]"
        )
        self.game.list_players()
        choice = typer.prompt("")
        choice = int(choice) - 1

        if choice >= len(self.game.players):
            self.game_view.display_error_message("Invalid choice")
            return self.choose_player()
        elif choice == self.game.current_player_index:
            self.game_view.display_error_message(
                "player can't perform action on themselves"
            )
            return self.choose_player()
        elif self.game.players[choice].state == PlayerState.OUT:
            self.game_view.display_error_message(
                f"{self.game.players[choice].name} is out of the game. Please choose another player."
            )
            return self.choose_player()
        else:
            self.game_view.display_message(
                f"{self.game.players[self.game.current_player_index].name} chose {style_text(self.game.players[choice].name)}"
            )
            return self.game.players[choice]

    def choose_card(self):
        hidden_cards = [
            card for card in self.cards if card["state"] != CardState.VISIBLE
        ]
        if len(hidden_cards) == 1:
            self.chosen_card = hidden_cards[0]
            self.chosen_card["state"] = CardState.VISIBLE
            return self.chosen_card

        table = Table("Choice", "Card", "State")
        for i, card in enumerate(self.cards):
            table.add_row(str(i + 1), style_text(card["name"]), str(card["state"]))

        self.game_view.display_table(table)

        self.game_view.display_message(
            f"[yellow]Which card would {self.name} like to choose?[/yellow]"
        )

        choice = random.randint(0, len(self.cards) - 1)

        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            self.chosen_card = self.cards[choice]
            self.chosen_card["state"] = CardState.VISIBLE
            return self.chosen_card
        else:
            choice = int(typer.prompt("")) - 1

        if choice >= len(self.cards):
            self.game_view.display_error_message("Invalid choice")
            return self.choose_card(self)

        self.chosen_card = self.cards[choice]
        self.chosen_card["state"] = CardState.VISIBLE

        return self.chosen_card

    def decide_challenge(self):
        self.game_view.display_message(
            f"[yellow]Would {self.name} like to challenge? (y/n)[/yellow]"
        )
        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            choice = random.randint(0, 1)
            if choice == 0:
                return False
            else:
                return True

        choice = typer.prompt("")

        if choice == "y":
            return True
        elif choice == "n":
            return False
        else:
            self.game_view.display_error_message("Invalid choice")
            return self.decide_challenge()

    def decide_block(self):
        self.game_view.display_message(
            f"[yellow]Would {self.name} like to block? (y/n)[/yellow]"
        )
        if self.type == "bot":
            time.sleep(BOT_THINK_TIME)
            choice = random.randint(0, 1)
            if choice == 0:
                return False
            else:
                return True

        choice = typer.prompt("")

        if choice == "y":
            return True
        elif choice == "n":
            return False
        else:
            self.game_view.display_error_message("Invalid choice")
            return self.decide_block()

    def challenge(self, sender_player):
        self.game_view.display_empty_line()
        self.game_view.display_message(
            f"[yellow]{self.name} challenged {sender_player.name}[/yellow]"
        )

        if self.type == "bot":
            chosen_card = random.choice(self.cards)
            self.game_view.display_message(
                f"{self.name} chose to reveal {style_text(chosen_card['name'])}"
            )
        else:
            self.game_view.display_message(
                f"[yellow]Which card would {sender_player.name} like to reveal?[/yellow]"
            )
            sender_player.choose_card()
            chosen_card = sender_player.chosen_card

        if chosen_card["name"] == sender_player.chosen_action["character"]:
            self.game_view.display_message(
                f"{sender_player.name} successfully revealed {style_text(sender_player.chosen_action['character'])}"
            )
            return False
        else:
            self.game_view.display_message(
                f"{sender_player.name} failed to reveal {style_text(sender_player.chosen_action['character'])}"
            )
            return True

    def income(self):
        self.game.players[self.game.current_player_index].coins += 1
        self.game_view.display_message(
            f"[grey70]{self.name} now has {coins_text(self.game.players[self.game.current_player_index].coins)}[/grey70]"
        )

    def foreign_aid(self):
        self.game.players[self.game.current_player_index].coins += 2
        self.game_view.display_message(
            f"[grey70]{self.name} will {style_text(self.chosen_action['description'])}[/grey70]"
        )
        self.game_view.display_empty_line()

    def coup(self):
        if self.game.players[self.game.current_player_index].coins < 7:
            self.game_view.display_message(
                f"{self.name} don't have enough {style_text('coins')} to coup. Please choose another action."
            )
            self.choose_action()
            return

        self.game.players[self.game.current_player_index].coins -= 7
        self.rec_player = self.choose_player()

        self.game_view.display_message(
            f"[yellow]{self.name} paid {coins_text(7)} to do a coup on {self.rec_player.name}[/yellow]"
        )
        self.rec_player.choose_card()
        self.game_view.display_message(
            f"[yellow]{self.rec_player.name} revealed {style_text(self.rec_player.chosen_card['name'])}[/yellow]"
        )

    def assassinate(self):
        global os

        if self.game.players[self.game.current_player_index].coins < 3:
            self.game_view.display_message(
                f"{self.name} doesn't have enough {style_text('coins')} to {style_text('assassinate')}. Please choose another action."
            )
            self.choose_action()
            return

        self.game.players[self.game.current_player_index].coins -= 3
        self.rec_player = self.choose_player()
        os.system("clear")
        self.game_view.display_message(
            f"[yellow]{self.name} chose to {style_text('assassinate')} {self.rec_player.name}[/yellow]"
        )
        self.game_view.display_empty_line()

    def tax(self):
        self.game.players[self.game.current_player_index].coins += 3
        self.game_view.display_message(
            f"[grey70]{self.name} will take {coins_text(3)}[/grey70]"
        )

    def exchange(self):
        if DEBUG:
            self.game_view.display_debug_message("[DEBUG] exchange started")

        self.game_view.display_message(f"[yellow]{self.name} pulled these cards.")
        new_cards = [self.game.deck.get_next_card(), self.game.deck.get_next_card()]
        new_cards = self.cards + new_cards
        self.game_view.display_message(Deck.cards_to_list(new_cards))

        self.game_view.display_message(
            f"[yellow]Which two would {self.name} like to keep? (e.g., 1 3)[/yellow]"
        )
        choice = self.input_action_exchange()

        try:
            selected_indices = [int(x) - 1 for x in choice.split()]

            if len(selected_indices) != 2 or not all(
                0 <= idx < len(new_cards) for idx in selected_indices
            ):
                self.game_view.display_error_message(
                    "Invalid selection. Please choose two distinct cards."
                )
            else:
                self.cards = [new_cards[idx] for idx in selected_indices]

                for idx, card in enumerate(new_cards):
                    if idx not in selected_indices:
                        self.game.deck.add_to_discard(card)
                self.game.deck.reshuffle_discard_into_deck()

        except ValueError:
            self.game_view.display_error_message(
                "Invalid input. Please enter two numbers separated by space."
            )

    def steal(self):
        if DEBUG:
            self.game_view.display_debug_message("[DEBUG] steal started")

        self.rec_player = self.choose_player()
        stolen_coins = 2
        if self.rec_player.coins < stolen_coins:
            stolen_coins = self.rec_player.coins

        self.coins += stolen_coins
        os.system("clear")
        self.game_view.display_message(
            f"{self.name} 1chose to {style_text('steal')} {coins_text(stolen_coins)} from {self.rec_player.name}"
        )

    def contessa(self):
        if DEBUG:
            self.game_view.display_debug_message("[DEBUG] contessa started")

        self.game_view.display_message(
            f"{self.name} chose to block assassination attempts"
        )
