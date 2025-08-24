import rich
from pyspotui.config import generic as generic
import random
import os


def header(text):
    rich.print("---- " + text + " ----")


def clear():
    """Clears the console screen."""
    os.system("clear")


def random_list_item(lst):
    """Returns a random item from the provided list."""
    if not lst:
        return None
    return random.choice(lst)


def log(message):
    """Logs a message to the log file."""
    with open("app.log", "a") as log_file:
        log_file.write(f"{message}\n")


class UI:
    def __init__(self, menu_options, hotkeys, startText=None, askForInputText=None):
        self.menu_options = menu_options
        self.hotkeys = hotkeys
        self.startText = startText if startText else generic.startText
        self.askForInputText = (
            askForInputText if askForInputText else generic.askForInputText
        )

    def display_menu(self, menu_options=None):
        """Displays the menu options."""
        if menu_options is None:
            menu_options = self.menu_options

        # Display start text with styling
        rich.print(self.startText)

        for i, option in enumerate(menu_options, start=1):
            if isinstance(option, dict):
                rich.print(f"{i}. {option['name']}")
            else:
                rich.print(f"{i}. {option}")

    def get_user_choice_and_run(self, menu_options=None):
        """Gets user choice and runs the corresponding function."""
        if menu_options is None:
            menu_options = self.menu_options
        else:
            self.menu_options = menu_options

        choice = input(self.askForInputText)
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(menu_options):
                selected_option = menu_options[choice_index]
                if isinstance(selected_option, dict) and "function" in selected_option:
                    selected_option["function"]()
                    if isinstance(selected_option, dict) and "value" in selected_option:
                        return selected_option["value"]
                elif isinstance(selected_option, dict) and "value" in selected_option:
                    return selected_option["value"]
                else:
                    rich.print(f"You selected: {selected_option}")
            else:
                rich.print("Invalid choice. Please try again.")
                self.get_user_choice_and_run(menu_options)
        except ValueError:
            # Check if choice is a keybind
            for keybind in self.hotkeys:
                if choice == keybind.get("combo"):
                    if "action" in keybind:
                        keybind["action"](self)
                    return
            rich.print("Invalid choice. Please try again.")
            self.get_user_choice_and_run(menu_options)


def hotkey_action_function_matcher(hotkeys, actions):
    """Matches hotkeys to their corresponding actions."""
    matched_actions = []
    for hotkey in hotkeys:
        for action in actions:
            if hotkey["action"] == action["name"]:
                matched_actions.append(
                    {"combo": hotkey["combo"], "action": action["function"]}
                )
    return matched_actions
