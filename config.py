import datetime
import json
import math
import os
import random
import re
import time
from enum import Enum

import typer
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.table import Column, Row, Table

from deck import *
from styles import *


class CardState(Enum):
    HIDDEN = 0
    VISIBLE = 1

    def __str__(self):
        return self.name.capitalize()


class PlayerState(Enum):
    OUT = 0
    PLAYING = 1
    TURN = 2

    def __str__(self):
        return self.name.capitalize()


class DisplayTableEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DisplayTable):
            return {
                "title": obj.title,
                "columns": obj.columns,
                "rows": obj.rows,
            }
        elif isinstance(obj, Column):
            return {
                "header": obj.header,
                "justify": obj.justify,
            }
        elif isinstance(obj, Row):
            return {
                "style": obj.style,
            }
        elif isinstance(obj, Table):
            return {
                "title": obj.title,
                "columns": obj.columns,
                "rows": obj.rows,
            }
        return super().default(obj)


class DisplayTable:
    def __init__(self, title):
        self.title = title
        self.columns = []
        self.rows = []

    def add_column(self, header, justify="left"):
        self.columns.append(Column(header, justify=justify))

    def add_row(self, *args):
        self.rows.append(Row(*args))

    def __str__(self):
        return {
            "title": self.title,
            "columns": self.columns,
            "rows": self.rows,
        }


# Load .env file
load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]
WRITE_LOG = os.getenv("WRITE_LOG", "True").lower() in ["true", "1"]
CHEAT_SEE_ALL_CARDS = os.getenv("CHEAT_SEE_ALL_CARDS", "False").lower() in ["true", "1"]
BOT_THINK_TIME = float(os.environ.get("BOT_THINK_TIME", 1.0))

console = Console()


def coins_display(coins):
    if coins == 1:
        return "coin"
    else:
        return "coins"


def coins_text(coins):
    return f"[grey70]{coins} {coins_display(coins)}[/grey70]"


def cli_spacing():
    typer.echo("")
    typer.echo("")
