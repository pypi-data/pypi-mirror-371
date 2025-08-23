from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def execute(playerData, amount):
    try:
        amount = int(amount)
        if amount <= 0:
            console.print(Panel("Please enter a valid amount to withdraw.", style="red", box=box.ROUNDED))
            return
        if amount > playerData.get('bank_balance', 0):
            console.print(Panel(f"You cannot withdraw more than your current bank balance of ${playerData['bank_balance']}.",
                                style="red", box=box.ROUNDED))
            return
        playerData['bank_balance'] -= amount
        playerData['balance'] += amount
        console.print(Panel(f"Successfully withdrew [bold green]${amount}[/bold green].",
                            style="green", box=box.DOUBLE))
    except ValueError:
        console.print(Panel("Invalid amount. Please enter a numeric value.", style="red", box=box.ROUNDED))