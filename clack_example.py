from pyclack import Clack, Colors, Theme
import time, os

def task1():
    time.sleep(2)  # Simulate work
    return "Task 1 complete"
def task2():
    time.sleep(3)  # Simulate work
    return "Task 2 complete"

def test_function(libs):
    # Do something with the selected libraries
    time.sleep(2)
    return "Installation complete"

def test_function_edit(libs):
    time.sleep(2)
    return "Installation complete"


@Clack.validator
def path_validator(response):
    if response[0] != ".":
        return False, "Input must be a valid path."

@Clack.validator
def length_validator(response):
    if len(response) < 5:
        return False, "Input must be at least 5 characters long."

@Clack.validator
def capital_letter_validator(response):
    if not response[0].isupper():
        return False, "Input must start with a capital letter."

p = Clack()
p.set_theme("DEFAULT")
p.intro("Sample Title")
p.group({
    "path": lambda responses:
        p.text(
            question = f"Where should we create your project?",
            placeholder = "./sparkling-solid",
            validators = [path_validator]
        ),

    "pwd": lambda responses:
        p.password(
            question = f"Provide a password",
            placeholder = "this is a secret",
            validators = [length_validator, capital_letter_validator]
        ),

    "libs": lambda responses:
        p.select(
            question = f"Pick a library to get started on {responses.get('path')}",
            options = [
                {'label': 'numpy', 'value': "numpy"},
                {'label': 'pandas', 'value': "pandas"},
                {'label': 'Flask', 'value': "flask"},
                {'label': 'Selenium', 'value': "selenium"},
                {'label': 'Tkinter', 'value': "tk", 'hint': 'oh no'},
            ],
            initial_value = ["flask"],
            # cursor_at = 3,
            max_items = 4,
        ),

    "tools": lambda responses:
        p.multiselect(
            question = f"Pick additional tools",
            options = [
                {'label': 'Pytest', 'value': "pytest", 'hint': 'recommended'},
                {'label': 'Docker', 'value': "docker", 'hint': 'recommended'},
                {'label': f'{p.link("https://github.com/psf/black", label="Black", options={"color": None})}', 'value': "black"},
            ],
            initial_values = ["pytest", "docker"],
            max_items = 3,
            cursor_at = 3,
        ),

    "group": lambda responses:
        p.group_multiselect(
            question = "Choose multiple elements or groups from this gruped options list",
            options = {
                'Group 1': {
                    'items': [{'label': 'item 1', 'value': '1.1'}, {'label': 'item 2', 'value': '1.2'}],
                    'hint': 'Group 1 hint'
                },
                'Group 2': {
                    'items': [{'label': 'item 2', 'value': '2.1', 'hint': 'cute hint for you'}, {'label': 'item 2', 'value': '2.2'}],
                }
            },
            initial_values=[],
            cursor_at='1.1',
        ),

    "install": lambda responses:
        p.confirm(
            question = "Install packages?",
            initial_value = True,
        ),

    "spinner": lambda responses:
        p.spinner(
            message = "Downloading packages...",
            function = test_function,
            args=(responses.get("libs"),)
        )
        if responses.get("install") == True else None, # or p.skip()

    "spinner_group": lambda responses:
        p.spinner_group(
            spinners = [
                p.spinner(
                    message = "Downloading packages...",
                    function = test_function,
                    args=(["numpy", "pandas"],)
                ),
                p.spinner(
                    message = "Running task 1",
                    function = task1,
                    args=(),
                ),
                p.spinner(
                    message = "Running task 2",
                    function = task2,
                    args=(),
                )
            ],
            message="Completing the last steps for you...",
            finish_message="All set! "
        ),

    },
    on_cancel = lambda: p.outro("You pressed Ctrl+C. Bye!"),
)

p.note("What next", "Support the creator: \n- leave a star")
p.outro(f"Problems? {p.link('https://github.com/Bbalduzz/pyclack')}")
p.prompt()

print("clack results:", p.form_results)
