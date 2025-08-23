import os
from rich.console import Console
from rich.panel import Panel
from rich import box
from lineage_rpg.schema import DATA_SCHEMA

console = Console()

def execute(playerData):
    playerData.clear()
    playerData.update(DATA_SCHEMA)
    console.print(Panel("Data successfully wiped!", style="green", box=box.DOUBLE))
