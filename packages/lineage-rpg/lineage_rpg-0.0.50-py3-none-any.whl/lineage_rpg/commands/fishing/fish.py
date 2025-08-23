import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich import box
from constants.fish_data import FISH_DATA

console = Console()

def weighted_size(min_w, max_w):
    r = random.random()
    return round(min_w + (max_w - min_w) * (r ** 2), 2)

DOTS = ["", ".", "..", "..."]

def execute(playerData):
    bait = playerData.get("bait")
    if bait:
        bait = bait.lower()
    if bait not in FISH_DATA:
        bait = None

    if bait and "inventory" in playerData and playerData["inventory"].get(bait, 0) > 0:
        playerData["inventory"][bait] -= 1
        if playerData["inventory"][bait] <= 0:
            del playerData["inventory"][bait]

    wait_time = random.uniform(2.0, 5.0) if bait else random.uniform(8.0, 12.0)
    console.print(Panel(f"You cast your fishing rod using [bold]{bait or 'no bait'}[/bold]...", style="cyan", border_style="blue", box=box.ROUNDED))

    start_time = time.time()
    frame_index = 0
    with Live("", refresh_per_second=4) as live:
        while time.time() - start_time < wait_time:
            dot = DOTS[frame_index % len(DOTS)]
            live.update(Text(f"The water ripples quietly{dot}", style="bright_cyan"))
            time.sleep(0.5)
            frame_index += 1

    console.print("\n[bold yellow]Something tugs on the line![/bold yellow]\n")
    time.sleep(1)

    success_chance = 0.8 if bait else 0.6
    if random.random() > success_chance:
        console.print(Panel("The fish slipped away before you could reel it in.", style="red", border_style="red", box=box.ROUNDED))
        return

    roll = random.random()
    cumulative = 0
    catch = None
    min_w, max_w = 0, 0
    for fish, chance, min_kg, max_kg in FISH_DATA[bait]:
        cumulative += chance
        if roll <= cumulative:
            catch = fish
            min_w, max_w = min_kg, max_kg
            break

    if not catch:
        console.print(Panel("You felt a tug, but nothing was caught.", style="red", border_style="red", box=box.ROUNDED))
        return

    weight = weighted_size(min_w, max_w)
    if "aquarium" not in playerData:
        playerData["aquarium"] = []
    playerData["aquarium"].append({"name": catch, "weight": weight})

    console.print(Panel(f"You caught a [bold green]{catch}[/bold green] weighing [bold]{weight} kg[/bold]!\nIt has been added to your aquarium.", style="green", border_style="green", box=box.DOUBLE))
