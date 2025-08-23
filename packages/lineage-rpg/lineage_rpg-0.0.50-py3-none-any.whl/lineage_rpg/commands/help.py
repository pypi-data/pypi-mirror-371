from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def execute(playerData):
    commands = [
        ("help", "View all commands"),
        ("balance", "Check your current balance"),
        ("bank", "Check your bank balance"),
        ("deposit <amount>", "Deposit money into your bank"),
        ("withdraw <amount>", "Withdraw money from your bank"),
        ("aquarium <show/sell>", "View or sell your fish in the aquarium"),
        ("exit", "Exit the game"),
    ]

    lines = [f"~ [bold yellow]{cmd}[/bold yellow] - {desc}" for cmd, desc in commands]
    panel_text = "\n".join(lines)

    console.print(Panel(panel_text,
                        title="[bold blue]Available Commands[/bold blue]",
                        border_style="bright_cyan",
                        box=box.DOUBLE))
