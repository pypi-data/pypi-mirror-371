from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def execute(playerData, amount):
    try:
        amount = int(amount)
        if amount <= 0:
            console.print(Panel("Please enter a valid amount to deposit.", style="red", box=box.ROUNDED))
            return
        if amount > playerData.get('balance', 0):
            console.print(Panel(f"You cannot deposit more than your current balance of ${playerData['balance']}.",
                                style="red", box=box.ROUNDED))
            return
        playerData['balance'] -= amount
        playerData['bank_balance'] += amount
        console.print(Panel(f"Successfully deposited [bold green]${amount}[/bold green].",
                            style="green", box=box.DOUBLE))
    except ValueError:
        console.print(Panel("Invalid amount. Please enter a numeric value.", style="red", box=box.ROUNDED))