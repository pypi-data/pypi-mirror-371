import os
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def execute(playerData, amount):
    playerData["balance"] = int(amount)
    console.print(Panel(f"Balance successfully set to [bold green]{amount}[/bold green]!", style="green", box=box.DOUBLE))