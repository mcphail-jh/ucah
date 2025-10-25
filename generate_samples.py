'''
Script which calls the Sampler class to create LHS samples from a parameterized CAD
'''
def main():
    import os
    from sampling import Sampler
    # -------------- FIRST -------------------
    # Create a folder in Documents with the same name as your CAD file. Change PROJECT_NAME to the name of this folder
    # Place the inputs excel file and CAD part in this folder

    # --------- EDIT THESE PARAMETERS --------
    NUM_SAMPLES = 45  # Number of configurations to generate
    NUM_DECIMALS = 3 # only considers samples up to `NUM_DECIMALS` decimals
    PROJECT_NAME = "parametric_v6" # name of the project folder in Documents
    INPUT_FILE = 'param_template.xlsx' # name of the excel file holding the parameters and bounds
    
    project_folder = os.path.expanduser(f'~/Documents/{PROJECT_NAME}')
    export_folder = os.path.join(project_folder, 'CAD')
    os.makedirs(export_folder, exist_ok=True)
    input_file = os.path.join(project_folder, INPUT_FILE)
    
    sampler = Sampler()
    sampler.import_params(input_file)
    sampler.lhs(NUM_SAMPLES, NUM_DECIMALS)
    sampler.export(PROJECT_NAME, export_folder)

if __name__ == "__main__":
    main()