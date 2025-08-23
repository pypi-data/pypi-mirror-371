from importlib.metadata import version, PackageNotFoundError
from inspect import signature
import sys
import os
import importlib
import pyfiglet

modules_to_reload = ['data', 'commands', 'schema']
for module_name in modules_to_reload:
    if module_name in sys.modules:
        del sys.modules[module_name]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data

_module_cache = {}
_signature_cache = {}

def _get_command_module(command):
    if command not in _module_cache:
        _module_cache[command] = importlib.import_module(f"commands.{command}")
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

def start_game():
    banner = pyfiglet.figlet_format("Lineage RPG", font="slant")
    print(f"{banner}\nType 'exit' or CTRL+C to quit.\nNote: Lineage RPG is still in early development, so expect bugs and incomplete features.\n")
    
    player_data = data.load_save()
    
    EXIT_COMMANDS = {"exit", "quit"}
    SEPARATOR = '\n' + '-' * 40 + '\n'

    try:
        while True:
            user_input = input("> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in EXIT_COMMANDS:
                print("Saving progress and exiting...")
                break

            try:
                cmd_module = _get_command_module(command)
                required_count, max_count = _get_command_signature(cmd_module)

                if len(args) < required_count:
                    print(f"Too few arguments for '{command}'. Expected at least {required_count}.\n")
                    continue

                if len(args) > max_count:
                    print(f"Too many arguments for '{command}'. Expected at most {max_count}.\n")
                    continue

                print(SEPARATOR)
                cmd_module.execute(player_data, *args)
                print(SEPARATOR)
                data.save_data(player_data)

            except ModuleNotFoundError:
                print(f"Unknown command: {command}\n")
            except Exception as e:
                print(f"An error occurred while executing '{command}': {e}\n")

    except KeyboardInterrupt:
        print("\nSaving progress and exiting...")
        data.save_data(player_data)
    except Exception as e:
        print(f"\nUnexpected error: {e}. Saving progress and exiting...")
        data.save_data(player_data)

if __name__ == "__main__":
    start_game()