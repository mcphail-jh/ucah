'''
Object representing one case/configuration to be ran by Fluent
'''
import os

class Case():

    def __init__(self, name, remote_path):
        self.name = name
        # this is the REMOTE ONEDRIVE PATH not a local path
        self.remote_path = remote_path
        # local path (if applicable)
        self.local_path = None
        # Indicates whether the case has been ran
        # Options: NOT DONE, IN PROGRESS, DONE
        self.status = None
        self.locked = False

    def __str__(self):
        string = f"{self.name}: {self.status}"
        if self.locked:
            string += " (LOCKED)"
        return string

    def set_status(self, status):
        self.status = status
    
    def set_local_path(self, local_path):
        self.local_path = local_path

    def lock(self):
        '''
        Takes a case folder name, and adds a lock.txt file
        '''
        # create empty lock.txt file
        with open(f"{self.remote_path}\\lock.txt", 'w') as f:
            pass
        self.locked = True

    def unlock(self):
        '''
        Takes a case folder name, and removes the lock.txt file from it
        '''
        try:
            lock_path = f"{self.remote_path}\\lock.txt"
            # remove lock.txt file
            if os.path.exists(lock_path):
                os.remove(lock_path)
        except OSError as e:
            print(f"Error deleting lock in '{self.name}': {e}")
        else:
            print(f"Case '{self.name}' was not locked.")
        
        self.locked = False
