from mesh import *
'''
Script to mesh every step file in a folder. Run with no command line arguments and a window will pop up to select the folder manually.
'''
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
    

if __name__ == "__main__":
    #folder = _choose_folder_via_dialog()
    folder = r"C:\Users\psh8ce\Documents\control_surface\CAD"
    for file in os.listdir(folder):
        if file.lower().endswith('step'):
            file_path = os.path.join(folder, file)
            named_selections_path = name_selections_symmetrical(file_path)
            mesh(named_selections_path)

