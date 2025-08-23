from importlib.metadata import version, PackageNotFoundError
from inspect import signature
import sys
import os
import importlib
import pkgutil
import pyfiglet
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.color import Color
from rich.style import Style

console = Console()

modules_to_reload = ['data', 'commands', 'schema']
for module_name in modules_to_reload:
    if module_name in sys.modules:
        del sys.modules[module_name]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data

_command_map = {}
_module_cache = {}
_signature_cache = {}

def _discover_commands():
    package = "commands"
    package_path = os.path.join(os.path.dirname(__file__), package)
    for _, modname, ispkg in pkgutil.walk_packages([package_path], package + "."):
        if ispkg:
            continue
        cmd_name = modname.split(".")[-1].lower()
        _command_map[cmd_name] = modname

_discover_commands()

def _get_command_module(command):
    command = command.lower()
    if command not in _command_map:
        raise ModuleNotFoundError(f"No command named {command}")
    modname = _command_map[command]
    if command not in _module_cache:
        module = importlib.import_module(modname)
        if not hasattr(module, "execute"):
            raise AttributeError(f"Module {modname} has no execute() function")
        _module_cache[command] = module
    return _module_cache[command]

def _get_command_signature(cmd_module):
    module_id = id(cmd_module)
    if module_id not in _signature_cache:
        sig = signature(cmd_module.execute)
        required_count = sum(
            1 for p in list(sig.parameters.values())[1:]
            if p.default is p.empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)
        )
        max_count = len(sig.parameters) - 1
        _signature_cache[module_id] = (required_count, max_count)
    return _signature_cache[module_id]

def print_banner():
    banner = pyfiglet.figlet_format("Lineage RPG", font="slant")
    in_vscode = "VSCODE_PID" in os.environ or "TERM_PROGRAM" in os.environ and os.environ["TERM_PROGRAM"] == "vscode"
    try:
        if in_vscode:
            console.print(banner, style="bold magenta", highlight=False, soft_wrap=True)
        else:
            for char in banner:
                console.print(char, end="", style="bold magenta", highlight=False, soft_wrap=True)
                time.sleep(0.005)
    except KeyboardInterrupt:
        console.print("\n[bold red]Banner animation interrupted. Exiting...[/bold red]")
        sys.exit(0)
    print()
    subtitle = Text("Type 'exit' or CTRL+C to quit. Type 'help' for a list of commands.", style="bold cyan")
    console.print(subtitle)
    console.print(Panel.fit(
        "[yellow]It is heavily recommended to play with the newest version.[/yellow]\n"
        "[red]Note: Lineage RPG is still in early development, so expect bugs and incomplete features.[/red]",
        title="[bold green]Welcome![/bold green]",
        border_style="bright_blue",
        box=box.DOUBLE,
    ))
    print()

def print_separator():
    console.print("\n" + "-" * 40 + "\n", style="dim")

def print_error(msg):
    print()
    console.print(Panel(msg, style="bold red", border_style="red", box=box.ROUNDED))
    print()

def print_success(msg):
    print()
    console.print(Panel(msg, style="bold green", border_style="green", box=box.ROUNDED))
    print()

def start_game():
    print_banner()
    player_data = data.load_save()
    EXIT_COMMANDS = {"exit", "quit", "abort"}
    try:
        while True:
            try:
                user_input = Prompt.ask("[bold blue]>[/bold blue]").strip()
            except EOFError:
                user_input = "exit"
            if not user_input:
                continue
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]
            if command in EXIT_COMMANDS:
                console.print("\n[bold green]Saving progress and exiting...[/bold green]\n")
                break
            try:
                cmd_module = _get_command_module(command)
                required_count, max_count = _get_command_signature(cmd_module)
                if len(args) < required_count:
                    print_error(f"Too few arguments for '[yellow]{command}[/yellow]'. Expected at least {required_count}.")
                    continue
                if len(args) > max_count:
                    print_error(f"Too many arguments for '[yellow]{command}[/yellow]'. Expected at most {max_count}.")
                    continue
                print_separator()
                cmd_module.execute(player_data, *args)
                print_separator()
                data.save_data(player_data)
            except ModuleNotFoundError:
                print_error(f"Unknown command: [yellow]{command}[/yellow]")
            except Exception as e:
                print_error(f"An error occurred while executing '[yellow]{command}[/yellow]': {e}")
    except KeyboardInterrupt:
        console.print("\n[bold green]Saving progress and exiting...[/bold green]\n")
        data.save_data(player_data)
    except Exception as e:
        print_error(f"Unexpected error: {e}. Saving progress and exiting...")
        data.save_data(player_data)

if __name__ == "__main__":
    start_game()
