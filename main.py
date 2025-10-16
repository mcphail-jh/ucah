'''
Main function to interact with the automation program.

--- Existing Functionality ---
Uploading New Cases
* After LHS is generated and IGS files are exported to project's CAD subfolder, upload files to OneDrive
Running Cases
* Specify # of cases and project folder. CaseManager pulls # of cases locally. Passes Case objects to fluent_auto

'''

import argparse
import os
import sys

def _parse_args():
    parser = argparse.ArgumentParser(description='Automation program CLI')
    # If --upload is present without an argument, argparse will set it to '' (const).
    parser.add_argument('--upload', nargs='?', const='', help='Upload CAD from project folder. Optionally provide path; omit to choose via dialog.')
    return parser.parse_args()

def _choose_folder_via_dialog():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title='Select project folder')
        root.destroy()
        return folder
    except Exception as e:
        print('Error opening folder dialog:', e, file=sys.stderr)
        return ''

def main():
    args = _parse_args()

    if args.upload is not None:
        project_folder = args.upload
        if project_folder == '':
            project_folder = _choose_folder_via_dialog()
            if not project_folder:
                print('No folder selected. Exiting.', file=sys.stderr)
                return

        if not os.path.isdir(project_folder):
            print(f'Provided path is not a directory: {project_folder}', file=sys.stderr)
            return

        try:
            from CaseManager import CaseManager
        except Exception as e:
            print('Failed to import CaseManager:', e, file=sys.stderr)
            return

        manager = CaseManager(project_folder)
        manager.upload_cad()
        return

    # ...existing code...
    return


if __name__ == '__main__':
    main()

'''
ChatGPT solution
import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

def select_project_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    path = filedialog.askdirectory(title="Select Project Folder")
    return Path(path) if path else None

def create_new_project():
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        return None

    base_path = select_project_path()
    if not base_path:
        print("No folder selected.")
        return None

    project_path = base_path / project_name
    try:
        project_path.mkdir(parents=True, exist_ok=False)
        (project_path / "CAD").mkdir()
        (project_path / "CFD").mkdir()
        print(f"Created project at: {project_path}")
        return project_path
    except FileExistsError:
        print("Project folder already exists.")
        return None
    except Exception as e:
        print(f"Error creating project folders: {e}")
        return None

def main():
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
        print(f"Using project path from command line: {project_path}")
    else:
        print("No project path specified.")
        print("Select with file dialog (1) or create new (2): ", end="")
        choice = input().strip()

        if choice == "1":
            project_path = select_project_path()
            if project_path:
                print(f"Selected project path: {project_path}")
            else:
                print("No path selected. Exiting.")
                return
        elif choice == "2":
            project_path = create_new_project()
            if not project_path:
                print("Failed to create project. Exiting.")
                return
        else:
            print("Invalid option. Exiting.")
            return

    # At this point, project_path is defined
    print(f"Project path is: {project_path}")
    # Wait for further instruction (you can insert additional logic here later)

if __name__ == "__main__":
    main()

'''