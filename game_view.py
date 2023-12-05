import typer
from rich.console import Console
from rich.table import Table

from config import coins_text
from styles import style_text


class GameView:
    def __init__(self):
        self.console = Console()
        self.game = None

    def cli_spacing(self):
        typer.echo("")

    def display_message(self, message):
        self.console.print(message)

    def get_user_input(self, prompt):
        return input(prompt)

    def display_table(self, table):
        self.console.print(table)

    def display_players(self):
        self.console.print("")
        self.console.print("Players:")

        table = Table("#", "Name", "Type", "Coins", "Cards", "Player State")
        for i, player in enumerate(self.game.players):
            table.add_row(
                str(i + 1),
                player.name,
                player.type,
                f"[grey70]{player.coins}[/grey70]",
                player.get_card_names(),
                str(player.state),
            )
        self.console.print(table)

    def display_game_over(self, winner):
        self.console.print(f"Game Over")
        self.console.print(f":trophy: {winner.name} wins! :trophy:")

    def display_turn_start(self, player):
        self.console.print(f"\n[bold]{player.name}[/bold]'s turn:")
        self.console.print(coins_text(player.coins))
        player.player_cards()

        self.display_players()

    def display_available_actions(self, player):
        self.console.print("\n[bold]Available Actions:[/bold]")
        table = Table("Choice", "Action", "Description", "Character")
        for i, action in enumerate(player.actions):
            table.add_row(
                str(i + 1),
                style_text(action["name"]),
                action["description"],
                style_text(action["character"]),
            )
        self.console.print(table)

    def display_visible_card_names(self, player):
        visible_card_names = self.display_player_cards(player)
        self.console.print("")

    def display_player_cards(self, player):
        self.console.print(f"[yellow]{player.name} has the following cards:[/yellow]")
        table = Table("Card", "State")
        for i, card in enumerate(player.cards):
            table.add_row(style_text(card["name"]), str(card["state"]))
        self.console.print(table)

    def display_empty_line(self, count=1):
        for _ in range(count):
            self.cli_spacing()

    def display_error_message(self, message):
        self.console.print(f"[red]Error: {message}[/red]")
