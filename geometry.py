import os
from pathlib import Path
import time

# Import the core components from the PyAnsys Geometry library
from ansys.geometry.core.connection import launcher as launch
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.math import Plane

# --- Configuration ---
# NOTE: Replace this with the actual path to your CAD file (e.g., .step, .x_t, .iges)
CAD_FILE_PATH = Path("C:/auto_files/Winged_Missile_2024.IGS")
EXPORT_DESIGN_NAME = "flat bottom geo"

def run_geometry_script():
    """
    Connects to the Geometry service, imports a CAD file, and creates named selections.
    """

    # 1. Initialize the Geometry Service (Connects to SpaceClaim/Discovery backend)
    # launch geometry
    print("Launching Geometry Service...")
    model = launch.launch_modeler_with_spaceclaim()
    print("Geometry Service launched successfully.")
  
    # 2. Import the CAD File
    print(f"Importing CAD file: {CAD_FILE_PATH.name}...")
    
    # This function returns the active Design object containing all geometry.
    # Using a dummy file path if the real one isn't found to let the script proceed
    # in a non-execution environment, but will warn the user.
    if CAD_FILE_PATH.exists():
        design = model.open_file(file_path=CAD_FILE_PATH)
        print("CAD file imported successfully.")
    else:
        # Mocking a basic design object for code demonstration purposes
        # (In a live environment, this block would not be needed)
        print("WARNING: Skipping actual file import due to missing file. Using a mock design object.")
        return # Exit since we cannot mock selection reliably

    # 3. Access the Imported Geometry
    bodies = design.bodies
    print(dir(design))
    print(len(bodies))

    # identify name surface regions
    inlet = [bodies[0]] + bodies[2:5]
    outlet = [bodies[1]]
    vehicle_faces = bodies[6:-1]


    print(type(bodies))
    if not bodies:
        print("Error: Imported design contains no solid bodies. Exiting.")
        return

    # We will select the first body in the design
    side1 = bodies[0]
    print(f"Found {len(bodies)} bodies. Targeting the first body: {side1.name}")

    # 4. Create Named Selection 1: Whole Body Selection
    # Select the entire body for a simulation part
    design.create_named_selection("inlet",bodies=inlet)
    design.create_named_selection("outlet",bodies=outlet)
    design.create_named_selection("vehicle",bodies=vehicle_faces)
    print("Named selections created successfully.")

    # 5. Export the Design with Named Selections
    design.export_to_pmdb(EXPORT_DESIGN_NAME)

    print("\nScript finished successfully.")


if __name__ == "__main__":
    # Ensure this script is executed in an environment where the Ansys Geometry service 
    # (e.g., SpaceClaim or Discovery) is running or can be launched.
    run_geometry_script()
