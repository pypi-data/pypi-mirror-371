from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

# 1. Show wallet balance
def execute(playerData):
    balance = playerData.get("balance", 0)
    console.print(Panel(f"[bold green]Balance:[/bold green] ${balance}\n\n"
                        "Use [bold]deposit <amount>[/bold] to deposit money into your bank or "
                        "[bold]withdraw <amount>[/bold] to withdraw money from your bank.",
                        title="[bold blue]Wallet[/bold blue]",
                        border_style="bright_cyan",
                        box=box.ROUNDED))