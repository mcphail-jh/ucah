
Prospective design process:
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
5. Create surrugate to predict performance of other designs
6. Evaluate/modify design for thermal/stability considerations
7. Run high-fidelity (CHORD) on finalized design.