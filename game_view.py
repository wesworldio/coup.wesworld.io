import typer
from rich.console import Console
from rich.table import Column, Row, Table

from config import DisplayTable, PlayerState, coins_text
from styles import style_text


class GameView:
    def __init__(self, game_log=None):
        self.console = Console()
        self.game_log = game_log
        self.game = None

    def cli_spacing(self):
        self.write_log("")  # Add an empty line to the log
        self.console.print("")  # Print the message

    def display_message(self, message):
        self.write_log(message)  # Write the message to the log
        self.console.print(message)  # Print the message

    def get_user_input(self, prompt):
        return input(prompt)

    def display_table(self, table):
        self.write_log(table)  # Write the table to the log
        self.console.print(table.to_rich_table()) # Print the table

    def display_debug_message(self, message):
        self.write_log(message)  # Write the table to the log
        self.console.print(message) # Print the table


    def display_players(self):
        self.write_log("Players:")

        table = DisplayTable("Players")
        table.add_column("#", justify="left")
        table.add_column("Name", justify="left")
        table.add_column("Type", justify="left")
        table.add_column("Coins", justify="left")
        table.add_column("Cards", justify="left")
        table.add_column("Player State", justify="left")
        table_data = []
        for i, player in enumerate(self.game.players):
            row = [
                str(i + 1),
                player.name,
                player.type,
                f"[grey70]{player.coins}[/grey70]",
                player.get_card_names(),
                str(player.state),
            ]
            table_data.append(row)
            table.add_row(row)

        self.display_table(table)

    def display_game_over(self, winner):
        message = f"\n[bold]Round {self.game.game_round}[/bold]\n\nGame Over\n:trophy: {winner.name} wins! :trophy:"
        self.display_message(message)

    def display_turn_start(self, player):
        message = f"\n[bold]Round {self.game.game_round}[/bold]\n[bold]{player.name}[/bold]'s turn:\n{coins_text(player.coins)}"
        self.display_message(message)
        player.player_cards()
        self.display_players()

    def display_available_actions(self, player):
        message = "\n[bold]Available Actions:[/bold]"
        actions_table = DisplayTable("Available Actions")
        actions_table.add_column("Choice", justify="left")
        actions_table.add_column("Action", justify="left")
        actions_table.add_column("Description", justify="left")
        actions_table.add_column("Character", justify="left")

        for i, action in enumerate(player.actions):
            actions_table.add_row(
                [
                    str(i + 1),
                    style_text(action["name"]),
                    action["description"],
                    style_text(action["character"]),
                ]
            )
        self.display_message(message)
        self.display_table(actions_table)

    def display_visible_card_names(self, player):
        card_names = self.display_player_cards(player)
        self.write_log("Visible Card Names:")
        for card_name in card_names:
            self.write_log(card_name)

    def display_player_cards(self, player):
        message = f"[yellow]{player.name} has the following cards:[/yellow]"
        cards_table = DisplayTable("Card State")
        cards_table.add_column("Card", justify="left")
        cards_table.add_column("State", justify="left")

        card_names = []
        for card in player.cards:
            cards_table.add_row([style_text(card["name"]), str(card["state"])])

        self.display_message(message)
        self.display_table(cards_table)
        return card_names

    def display_empty_line(self, count=1):
        for _ in range(count):
            self.cli_spacing()

    def display_error_message(self, message):
        error_message = f"Error: {message}"
        self.display_message(error_message)

    def write_log(self, log_message):
        if self.game_log:
            self.game_log.add_log(log_message)
