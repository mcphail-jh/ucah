## WORKFLOW

### Create LHS Samples
1. Create parametric CAD model
2. Use param_template.xlsx to input all parameter names (must be global variables) and their upper/lower bounds.
3. Run sampling.py. A project folder will be created in Documents with the LHS design table and JSON config files.
4. Place the CAD file into the project folder and open in SOLIDWORKS. Insert -> Design Table and select the generated design table.
5. Tools -> Macros -> Run `ExportConfigToIGS_25.swp`. All IGS files will be exported into the project folder.
5. (WIP) Run `CaseManager.py --upload "project_folder"` to upload these samples to our shared OneDrive. A folder will be made for each sample.

### Run Cases (WIP)
1. Run `CaseManager.py --checkout n` to download n files which need to be meshed and/or ran. It will mark those files as reserved so other machines don't re-run them.
2. CaseManager will attempt to automatically mesh and run each file in queue.
 - Data files will be saved along with a JSON summary including # of iterations and relevant values for the objective function.

### Summarize Results (WIP)
1. Run a script (or python for Excel?) to check each folder's status
2. Details will include whether or not the case has been meshed/ran, values from the summary JSON, and a timestamp of the last sync



### Prospective Design Process
1. Base Solidworks Part
    - Paramaterize + upper and lower bounds
2. LHS to get configurations
    - SciPy LHS -> Excel Sheet _> SW Design Config
    - Bad geometry deletion if possible.
3. SW part saving script
    - Naming Convention
    - format (IGES)
4. PyFluent CFD Job Scheduler + mesh gen
    - Load IGES, generate mesh, detect errors.
    - run, save HS, extract Lift/L/D, residuals
    - OUTPUT Excel w/ results of interest (L/D or other computed obj. func.)
5. Create surrogate to predict performance of other designs
6. Evaluate/modify design for thermal/stability considerations
7. Run high-fidelity (CHORD) on finalized design.