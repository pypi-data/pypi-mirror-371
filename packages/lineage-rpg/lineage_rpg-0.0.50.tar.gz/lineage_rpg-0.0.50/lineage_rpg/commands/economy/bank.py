from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def execute(playerData):
    bank_balance = playerData.get("bank_balance", 0)
    console.print(Panel(f"[bold green]Bank Balance:[/bold green] ${bank_balance}\n\n"
                        "Use [bold]deposit <amount>[/bold] to deposit money or "
                        "[bold]withdraw <amount>[/bold] to withdraw money.",
                        title="[bold blue]Bank[/bold blue]",
                        border_style="bright_magenta",
                        box=box.ROUNDED))