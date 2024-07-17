#!/usr/bin/python
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QFileDialog

def select_game_folder():
    app = QApplication(sys.argv)
    folder = QFileDialog.getExistingDirectory(None, "Select the game folder")
    if folder:
        return folder
    else:
        print("No folder selected.")
        sys.exit(1)

def find_python_executable(base_path):
    potential_dirs = ["py3-linux-x86_64", "py2-linux-i686"]
    for dir_name in potential_dirs:
        full_path = os.path.join(base_path, "lib", dir_name, "python")
        if os.path.isfile(full_path):
            return full_path
    print("Python executable not found.")
    sys.exit(1)

def find_game_script(base_path):
    py_files = [f for f in os.listdir(base_path) if f.endswith(".py")]
    if len(py_files) == 1:
        return os.path.join(base_path, py_files[0])
    elif len(py_files) > 1:
        print("Multiple .py files found. Unable to determine the correct game script.")
        sys.exit(1)
    else:
        print("No .py file found in the game folder.")
        sys.exit(1)

def main():
    game_folder = select_game_folder()
    python_executable = find_python_executable(game_folder)
    game_script = find_game_script(game_folder)

    translate_folder = os.path.join(game_folder, "translate", "spanish")
    os.makedirs(translate_folder, exist_ok=True)

    command = [
        python_executable,
        game_script,
        game_folder,
        "translate",
        "spanish"
    ]

    subprocess.run(command)

if __name__ == "__main__":
    main()


# -> Select the main folder of the game and wait few seconds, inside /tl folder you have a new folder to translate using the "translateador to pofesioná".



