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
# default name of the folder in the OneDrive where cases are stored
# change with set_db_name if another name is being used
DB_NAME = "TestDatabase"


class CaseManager():

    def __init__(self, project_folder):
        # project_folder will contain cfd_folder and cad_folder as subfolders
        self.project_folder = project_folder
        self.cfd_folder = os.path.join(project_folder, 'CFD')
        self.cad_folder = os.path.join(project_folder, 'CAD')

        # create the folders if they don't exist
        os.makedirs(self.cfd_folder, exist_ok=True)
        os.makedirs(self.cad_folder, exist_ok=True)

        # dictionary of each case on OneDrive. Format: {'case_name': 'DONE'/'IN PROGRESS'/'NOT DONE'}
        self.case_status = {}
        # stores the cases queued to be ran
        self.queue = []
        # name of the OneDrive database folder
        self.db_name = DB_NAME
        
        # check that OneDrive is signed in and has the proper shortcut
        if not os.path.isdir(os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\")):
            return "Error: Could not find OneDrive database.\nEnsure OneDrive is signed in and you have the UCAH Hypersonic Design Competition Capstone Group - Documents shortcut"
        
        self.onedrive_folder = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\" + DB_NAME)

    def _pull_remote_status(self):
        '''
        Checks OneDrive for the status of each case. Helpful for selecting cases which are not being worked on.
        '''
        new_cases = {}
        case_folders = os.listdir(self.onedrive_folder)
        for case in case_folders:
            case_path = os.path.join(self.onedrive_folder, case)
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


    def upload_cad(self):
        '''
        Uploads all IGES files from local `cad_folder` to separate folders in the team OneDrive 
        '''
        if not os.path.isdir(self.project_folder):
            print("Error: Invalid/Missing Project Folder: ", self.project_folder)
            return
        
        igs_files = [f for f in os.listdir(self.project_folder) if f.endswith('.igs') or f.endswith('.json')]

        for file in igs_files:
            # make a new folder with the file's name (minus the .igs suffix)
            destination_directory = os.path.join(self.onedrive_folder, file[:-4])

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

    
    def pull_cases(self, n_cases : int, lock=True):
        '''
        Function
        * Reserves and downloads CFD cases to be ran
        * Finds the first n folders which are NOT DONE (not locked or already done)
        * Calls `_download()` to copy the folders locally to `self.cfd_folder`
        * Adds cases to the queue

        `n_cases` - *int*
        * Number of cases to be pulled and queued
        
        `lock` - *bool* 
        * If True, adds a lock.txt file to the remote folder, preventing other users from running that case
        '''

        # get the latest status of the remote folders
        self._pull_remote_status()

        # loop through all cases
        selected_cases = []
        for case in self.case_status.keys():
            # select ones that are available
            if self.case_status[case] == "NOT DONE":
                selected_cases.append(case)
                print(f"Selected available case {case} ({len(selected_cases)}/{n_cases})")

                if lock:
                    self._lock(case)

                # download the files
                local_path = self._download(case)
                
                # append the full path to the queue
                self.queue.append(local_path)
            
            # stop when n cases have been selected
            if len(selected_cases) == n_cases:
                break
        
        return self.queue

    
    def _lock(self, case):
        '''
        Takes a case folder name, and adds a lock.txt file
        '''
        remote_path = os.path.join(self.onedrive_folder, case)
        # create empty lock.txt file
        with open(f"{remote_path}\\lock.txt", 'w') as f:
            pass

    def _unlock(self, case):
        '''
        Takes a case folder name, and removes the lock.txt file from it
        '''
        try:
            remote_path = os.path.join(self.onedrive_folder, case)
            lock_path = f"{remote_path}\\lock.txt"
            # remove lock.txt file
            if os.path.exists(lock_path):
                os.remove(lock_path)
        except OSError as e:
            print(f"Error deleting lock in '{case}': {e}")
        else:
            print(f"Case '{case}' was not locked.")
    

    def _download(self, folder_name):
        '''
        Helper function to download the contents of one folder from the OneDrive database into `self.cfd_folder`
        Returns the full path of the local folder
        '''
        # get full path to the new folder
        local_path = os.path.join(self.cfd_folder, folder_name)
        # make the new folder if it doesn't exist
        os.makedirs(local_path, exist_ok=True)

        # get full path to the remote file
        remote_path = os.path.join(self.onedrive_folder, folder_name)

        # Copy all the files
        for f in os.listdir(remote_path):
            source = os.path.join(remote_path, f)
            destination = os.path.join(local_path, f)
            try:
                shutil.copy(source, destination)
                print(f"File '{f}' copied successfully to '{remote_path}'")
            except FileNotFoundError:
                print(f"Error: Source file '{f}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        return local_path




    # ------------ setter functions ------------

    def set_db_name(self, db_name):
        self.db_name = db_name
        self.onedrive_folder = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\" + self.db_name)


if __name__ == '__main__':


    # test code
    '''
    manager = CaseManager('C:\\Users\\psh8ce\\Documents\\Prism')
    manager.upload()
    time.sleep(5)
    manager.pull_onedrive_status()
    print(manager.case_status)
    '''
