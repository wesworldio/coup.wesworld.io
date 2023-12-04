import re

styles = {
    "Ambassador": "[bold yellow4]Ambassador[/bold yellow4]",
    "Exchange": "[bold yellow4]Exchange[/bold yellow4]",
    "Assassin": "[bold grey30]Assassin[/bold grey30]",
    "Assassinate": "[bold grey30]Assassinate[/bold grey30]",
    "Captain": "[bold deep_sky_blue1]Captain[/bold deep_sky_blue1]",
    "Steal": "[bold deep_sky_blue1]Steal[/bold deep_sky_blue1]",
    "Contessa": "[bold red3]Contessa[/bold red3]",
    "Duke": "[bold deep_pink3]Duke[/bold deep_pink3]",
    "Tax": "[bold deep_pink3]Tax[/bold deep_pink3]",
    "coins": "[grey70]coins[/grey70]",
    "coin": "[grey70]coin[/grey70]",
}


def style_text(text):
    for word, style in styles.items():
        text = re.sub(rf"\b{word}\b", style, text)

    return text
