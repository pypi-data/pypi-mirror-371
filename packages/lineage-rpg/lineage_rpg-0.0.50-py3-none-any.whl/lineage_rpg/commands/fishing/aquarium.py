from rich.console import Console
from rich.panel import Panel
from rich import box
from constants.fish_data import FISH_PRICES

console = Console()

def execute(playerData, action="show"):
    aquarium = playerData.get("aquarium", [])
    if not aquarium:
        console.print(Panel("Your aquarium is empty.", style="yellow", box=box.ROUNDED))
        return

    action = action.lower()
    if action not in ["show", "sell"]:
        console.print(Panel("Invalid action. Use 'show' or 'sell'.", style="red", box=box.ROUNDED))
        return

    if action == "show":
        total_value = 0
        fish_lines = []
        for fish in aquarium:
            name = fish["name"]
            weight = fish["weight"]
            price_per_kg = FISH_PRICES.get(name, 5)
            value = int(weight * price_per_kg)
            total_value += value
            fish_lines.append(f"{name}: {weight} kg × ${price_per_kg}/kg = ${value}")

        panel_text = "\n".join(fish_lines)
        panel_text += f"\n\n[bold green]Total value: ${total_value}[/bold green]"
        console.print(Panel(panel_text, title="[bold blue]Aquarium[/bold blue]", box=box.DOUBLE, border_style="bright_cyan"))

    elif action == "sell":
        total_value = 0
        for fish in aquarium:
            name = fish["name"]
            weight = fish["weight"]
            price_per_kg = FISH_PRICES.get(name, 5)
            total_value += int(weight * price_per_kg)

        playerData["balance"] = playerData.get("balance", 0) + total_value
        aquarium.clear()

        console.print(Panel(f"You sold all your fish for [bold green]${total_value}[/bold green]!", 
                            title="[bold blue]Fish Sold[/bold blue]", box=box.DOUBLE, border_style="bright_cyan"))
