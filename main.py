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
    parser.add_argument('project_folder', nargs='?', const='', help='Path to project folder. Omit to choose via dialog.')
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
    try:
        args = _parse_args()

        project_folder = args.project_folder
        if project_folder == '' or project_folder is None:
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
        # start dialog to choose action
        print("------Welcome to LARP Automation------")
        print("Project folder set to:", project_folder)
        print('--------------------------------------')
        while True:
            action = input("Select Action: Upload CAD (1) | Run Cases (2) | Unlock All Cases (3) | Exit (any other key): ")
            if action == "1":
                manager.upload_cad()
            elif action == "2":
                n = int(input("Enter number of cases to pull: "))
                while n <= 0:
                    n = int(input("Please enter a valid positive integer for number of cases: "))

                # pull_cases returns a list of Case objects
                queue = manager.pull_cases(n)
                # TODO: Pass the queue to fluent_auto for processing



                if len(queue) == 0:
                    print("No available cases to run. Exiting.")
                    return
            elif action == "3":
                confirm = input("Are you sure? Only do this for debugging and NOT if anyone else is running cases.\n'y' to continue. Any other key to cancel.")
                if str(confirm) == 'y':
                    manager.unlock_all()

            else:
                print("Exiting.")
                return
    
    
    except KeyboardInterrupt:
        if queue is not None and len(queue) > 0:
            print("Releasing locks on pulled cases...")
            for case in queue:
                case.unlock()
    except Exception as e:
        if queue is not None and len(queue) > 0:
            print("Releasing locks on pulled cases...")
            for case in queue:
                case.unlock()
        print('An unexpected error occurred:', e, file=sys.stderr)
        


if __name__ == '__main__':
    main()
