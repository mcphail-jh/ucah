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
from fluentfile_auto import CFD_job
import time
import threading

CAD_EXT = '.step'
TIMEOUT_SEC = 30
logout = False

def _parse_args():
    parser = argparse.ArgumentParser(description='Automation program CLI')
    # If --upload is present without an argument, argparse will set it to '' (const).
    parser.add_argument('-l', action='store_true', help='If present, will logout after running')
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


def timeout_logout(queue):
        try:
            if queue is not None and len(queue) > 0:
                print("Releasing locks on pulled cases...")
                for case in queue:
                    case.unlock()
                print("Done.")
        finally:
            print("Logging out since timeout was exceeded")
            os.system('shutdown /l')


def main():
    queue = None

    try:

        args = _parse_args()
        #global logout
        #logout = args.l

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
        
        
        logout_input = input("Do you want to logout when done? (y/n): ")
        if logout_input == "y":
            timeout = int(input("How many seconds until logout?: "))
            global logout, TIMEOUT_SEC
            logout = True
            TIMEOUT_SEC = timeout


        if logout:
            timer = threading.Timer(TIMEOUT_SEC, timeout_logout, args=[queue])
            timer.start()
            print(f"Logout timer for {TIMEOUT_SEC} starting now")
        
        manager = CaseManager(project_folder)
        queue = None
        # start dialog to choose action
        print("------Welcome to LARP Automation------")
        print("Project folder set to:", project_folder)
        print('--------------------------------------')
        while True:
            action = input("Select Action: Upload CAD (1) | Run Cases (2) | Unlock All Cases (3) | Exit (any other key): ")
            if action == "1":
                manager.upload_cad()
            elif action == "2":
                n_procs = int(input("Enter number of processors: "))
                while n_procs <= 0:
                    n_procs = int(input("Please enter a valid positive integer for number of processors: "))
                
                n = int(input("Enter number of cases to pull: "))
                while n <= 0:
                    n = int(input("Please enter a valid positive integer for number of cases: "))
                
                n_iter = int(input("Enter number of iterations per case: "))
                while n_iter <= 0:
                    n_iter = int(input("Please enter a valid positive integer for number of iterations: "))

                # pull_cases returns a list of Case objects
                queue = manager.pull_cases(n)

                if len(queue) == 0:
                    print("No available cases to run. Exiting.")
                    return
                
                # TODO: Pass the queue to fluent_auto for processing
                # run each case and move on to the next one if it failed
                for i, case in enumerate(queue):
                    print(f"Running case {case.name} ({i+1}/{len(queue)})")
                    start_time = time.time()
                    try:
                        # TODO: Specify number of processors from command line
                        cfd_job = CFD_job(case.local_path, nprocs=n_procs)

                        # FOR RIGHT NOW, ASSUMING NO MESH FILE EXISTS AND ALL RUNS ARE FROM CAD
                        cad_path = [f for f in os.listdir(case.local_path) if f.lower().endswith(CAD_EXT)][0]
                        cad_path = os.path.join(case.local_path, cad_path)

                        # mesh and run case
                        cfd_job.run_fluent(cad_file=cad_path, iter=n_iter, adapt_frequency=2000)

                        # upload the results to the remote folder
                        manager._upload_case(case)

                        # allow time for the files to upload
                        time.sleep(10)

                        # if successful, delete the local folder to save space
                        manager.delete_local_folder(case)
                    
                    except Exception as e:
                        print(f"An error occured! {case.name}: {e}")
                    finally:
                        case.unlock()
                        end_time = time.time()
                        print(f"TOTAL TIME ELAPSED: {end_time - start_time} seconds")
                # if all cases ran successfully and -l is specified, exit and logout
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
            print("Done")
    except Exception as e:
        if queue is not None and len(queue) > 0:
            print("Releasing locks on pulled cases...")
            for case in queue:
                case.unlock()
            print("Done.")
        print('An unexpected error occurred:', e, file=sys.stderr)
    finally:
        if logout:
            print("Logging out since work ended")
            os.system('shutdown /l')
        


if __name__ == '__main__':
    main()
