"""
This is a class to sync local files (generated IGS files, local CFD runs) with a remote folder (the OneDrive cloud storage)
Given a path to a folder of IGS files and corresponding json config files, it will create/update corresponding folders in the team OneDrive folder

REQUIRED: To access the OneDrive foler, you must be logged into OneDrive and have the UCAH folder added as a shortcut. It's name should be: 
UCAH Hypersonic Design Competition Capstone Group - Documents

"""
import time
import shutil
import os
from Case import Case


RESULTS_FILE = 'output.json'
LOCK_FILE = 'lock.txt'
CAD_EXT = '.step'

# default name of the folder in the OneDrive where cases are stored
# can specify a different remote folder on initialization if desired (e.g. to work locally)
REMOTE_FOLDER = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\")
DB_NAME = "TestDatabase"


class CaseManager():

    def __init__(self, project_folder, remote_folder=REMOTE_FOLDER, db_name=DB_NAME):
        # project_folder will contain cfd_folder and cad_folder as subfolders
        self.project_folder = project_folder
        self.remote_folder = remote_folder
        self.cfd_folder = os.path.join(project_folder, 'CFD')
        self.cad_folder = os.path.join(project_folder, 'CAD')

        # create the folders if they don't exist
        os.makedirs(self.cfd_folder, exist_ok=True)
        os.makedirs(self.cad_folder, exist_ok=True)

        # List of Case objects pulled from OneDrive
        self.remote_cases = []

        # name of the OneDrive database folder
        self.db_name = db_name
        
        # check that OneDrive is signed in and has the proper shortcut
        if not os.path.isdir(remote_folder):
            return "Error: Could not find remote folder.\nEnsure OneDrive is signed in and you have the UCAH Hypersonic Design Competition Capstone Group - Documents shortcut"
        
        self.db_folder = os.path.join(remote_folder, db_name)

    def _update_remote_cases(self):
        '''
        Checks OneDrive database at `db_folder` for the status of each case. Helpful for selecting cases which are not being worked on.
        '''
        new_cases = []
        case_names = os.listdir(self.db_folder)
        for case_name in case_names:
            case_path = os.path.join(self.db_folder, case_name)
            # if the item is in fact a subfolder, open it
            if os.path.isdir(case_path):
                # create a new Case object
                case = Case(case_name, case_path)
                case_files = os.listdir(case_path)
                # if lock.txt is present, the case is IN PROGRESS
                if LOCK_FILE in case_files:
                    case.set_status('IN PROGRESS')
                    case.locked = True
                elif RESULTS_FILE in case_files:
                    case.set_status('DONE')
                else:
                    case.set_status('NOT DONE')

                new_cases.append(case)
        
        # overwrite list with updated cases
        self.remote_cases = new_cases


    def upload_cad(self):
        '''
        Uploads all IGES files from local `cad_folder` to separate folders in the team OneDrive `db_folder`
        '''
        print("Uploading CAD files to ", self.db_name)
        if not os.path.isdir(self.project_folder):
            print("Error: Invalid/Missing Project Folder: ", self.project_folder)
            return
        
        igs_files = [f for f in os.listdir(self.cad_folder) if f.endswith(CAD_EXT) or f.endswith('.json')]

        for file in igs_files:
            # make a new folder with the file's name (minus the extension)
            folder_name = file.split('.')[0]
            destination_directory = os.path.join(self.db_folder, folder_name)

            # Ensure the destination directory exists (optional, but good practice)
            os.makedirs(destination_directory, exist_ok=True)

            # get full path to the source file
            source_file = os.path.join(self.cad_folder, file)

            try:
                # Copy the file
                shutil.copy(source_file, destination_directory)
                #print(f"File '{source_file}' copied successfully to '{destination_directory}'")
            except FileNotFoundError:
                print(f"Error: Source file '{source_file}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        print(f"Uploaded {len(igs_files)//2} CAD file cases")
            

    
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
        # initialize list of selected cases to return
        queue = []
        # get the latest status of the remote folders
        self._update_remote_cases()

        # loop through all cases
        num_new_cases = 0
        for case in self.remote_cases:
            # select ones that are available
            if case.status == "NOT DONE":
                num_new_cases += 1
                print(f"Selected available case {case} ({num_new_cases}/{n_cases})")

                if lock:
                    case.lock()

                # download the files
                local_path = self._download_case(case.name)
                # assign local path to the case object and add to the queue
                case.set_local_path(local_path)
                queue.append(case)
            
            # stop when n cases have been selected
            if num_new_cases == n_cases:
                break
        
        return queue
    
    def unlock_all(self):
        '''
        Unlocks all locked cases in the OneDrive database by removing their lock.txt files
        '''
        self._update_remote_cases()
        for case in self.remote_cases:
            if case.locked:
                case.unlock()

    def force_unlock_all(self):
        '''
        Unlocks ALL cases in the OneDrive database by removing any lock.txt files
        '''
        self._update_remote_cases()
        for case in self.remote_cases:
            case.unlock()


    def _download_case(self, folder_name):
        '''
        Helper function to download the contents of one folder from the OneDrive database into `self.cfd_folder`
        Returns the full path of the local folder
        '''
        # get full path to the new folder
        local_path = os.path.join(self.cfd_folder, folder_name)
        # make the new folder if it doesn't exist
        os.makedirs(local_path, exist_ok=True)

        # get full path to the remote file
        remote_path = os.path.join(self.db_folder, folder_name)

        # Copy all the files
        for f in os.listdir(remote_path):
            source = os.path.join(remote_path, f)
            destination = os.path.join(local_path, f)
            try:
                shutil.copy(source, destination)
                #print(f"File '{f}' copied successfully to '{remote_path}'")
            except FileNotFoundError:
                print(f"Error: Source file '{f}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
        return local_path
    
    def _upload_case(self, case : Case):
        '''
        Helper function to upload the contents from the case's local folder to the remote folder
        '''
        # get full path to the new folder
        remote_path = case.remote_path
        # make the new folder if it doesn't exist
        os.makedirs(remote_path, exist_ok=True)

        # get full path to the local file
        local_path = case.local_path

        # Copy all the files
        for f in os.listdir(local_path):
            source = os.path.join(local_path, f)
            destination = os.path.join(remote_path, f)
            try:
                shutil.copy(source, destination)
                #print(f"File '{f}' copied successfully to '{remote_path}'")
            except FileNotFoundError:
                print(f"Error: Source file '{f}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
    

    # ------------ setter functions ------------

    def set_db_name(self, db_name):
        self.db_name = db_name
        self.db_folder = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\" + self.db_name)


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
