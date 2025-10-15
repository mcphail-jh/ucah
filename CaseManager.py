"""
This is a class to sync generated CFD cases (IGS files) with the OneDrive cloud storage
Given a path to a folder of IGS files and corresponding json config files, it will create/update corresponding folders in the team OneDrive folder

REQUIRED: You must be logged into OneDrive and have the UCAH folder added as a shortcut. It's name should be: 
UCAH Hypersonic Design Competition Capstone Group - Documents

"""
import time
import shutil
import os


RESULTS_FILE = 'output.json'
LOCK_FILE = 'lock.txt'
# real code will change this to 
DB_NAME = "TestDatabase"


class CaseManager():

    def __init__(self):

        self.project_folder = None
        # dictionary of each case on OneDrive. Format: {'case_name': 'DONE'/'IN PROGRESS'/'NOT DONE'}
        self.cases = {}
        
        # check that OneDrive is signed in and has the proper shortcut
        if not os.path.isdir(os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\")):
            return "Error: Could not find OneDrive database.\nEnsure OneDrive is signed in and you have the UCAH Hypersonic Design Competition Capstone Group - Documents shortcut"
        
        self.onedrive_dir = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\" + DB_NAME)


    def pull_cases(self):
        '''
        Checks OneDrive for the status of each case. Helpful for selecting cases which are not being worked on.
        '''
        new_cases = {}
        case_folders = os.listdir(self.onedrive_dir)
        for case in case_folders:
            case_path = os.path.join(self.onedrive_dir, case)
            # if the item is in fact a subfolder, open it
            if os.path.isdir(case_path):
                case_files = os.listdir(case_path)
                # case 1: if lock.txt is present, the case is IN PROGRESS
                if LOCK_FILE in case_files:
                    new_cases[case] = 'IN PROGRESS'
                # case 2: 
                elif RESULTS_FILE in case_files:
                    new_cases[case] = 'DONE'
                else:
                    new_cases[case] = 'NOT DONE'
        
        # overwrite dictionary with new values
        self.cases = new_cases


    def upload(self):
        '''
        Uploads all IGES files from local `project_folder` to separate folders in the team OneDrive 
        '''
        if not os.path.isdir(self.project_folder):
            print("Error: Invalid/Missing Project Folder: ", self.project_folder)
            return
        
        igs_files = [f for f in os.listdir(self.project_folder) if f.endswith('.igs') or f.endswith('.json')]

        for file in igs_files:
            # make a new folder with the file's name (minus the .igs suffix)
            destination_directory = os.path.join(self.onedrive_dir, file[:-4])

            # Ensure the destination directory exists (optional, but good practice)
            os.makedirs(destination_directory, exist_ok=True)

            # get full path to the source file
            source_file = os.path.join(self.project_folder, file)

            try:
                # Copy the file
                shutil.copy(source_file, destination_directory)
                print(f"File '{source_file}' copied successfully to '{destination_directory}'")
            except FileNotFoundError:
                print(f"Error: Source file '{source_file}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")


    # ------------ setter functions ------------
    def set_project_folder(self, project_folder):
        self.project_folder = project_folder


if __name__ == '__main__':
    # test code
    '''
    manager = CaseManager()
    manager.set_project_folder('C:\\Users\\psh8ce\\Documents\\Prism')
    manager.upload()
    time.sleep(5)
    manager.pull_cases()
    print(manager.cases)
    '''
