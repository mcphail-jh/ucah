import os
from pathlib import Path
import time

# Import the core components from the PyAnsys Geometry library
from ansys.geometry.core.connection import launcher as launch
from ansys.geometry.core.misc import UNITS, DEFAULT_UNITS

# --- Configuration ---
# NOTE: Replace this with the actual path to your CAD file (e.g., .step, .x_t, .iges)
ansys_version = 251
CAD_FILE_PATH = Path(os.path.join(os.getcwd(),"parametric_v4_box.STEP"))

def run_geometry_script():
    """
    Connects to the Geometry service, imports a CAD file, and creates named selections.
    """

    # 1. Initialize the Geometry Service (Connects to SpaceClaim/Discovery backend)
    # launch geometry
    print("Launching Geometry Service...")
    model = launch.launch_modeler_with_spaceclaim(product_version=ansys_version)
    print("Geometry Service launched successfully.")
  
    # 2. Import the CAD File
    print(f"Importing CAD file: {CAD_FILE_PATH.name}...")
    
    # This function returns the active Design object containing all geometry.
    # Using a dummy file path if the real one isn't found to let the script proceed
    # in a non-execution environment, but will warn the user.
    if CAD_FILE_PATH.exists():
        design = model.open_file(file_path=CAD_FILE_PATH)
        DEFAULT_UNITS.LENGTH = UNITS.m  # Set default units to meters
        print("CAD file imported successfully.")
    else:
        # Mocking a basic design object for code demonstration purposes
        # (In a live environment, this block would not be needed)
        print("WARNING: Skipping actual file import due to missing file. Using a mock design object.")
        return # Exit since we cannot mock selection reliably

    # 3. Access the Imported Geometry
    body = design.bodies[0]

    # identify name surface regions
    inlet = body.faces[0:3] + body.faces[4:6]
    outlet = [body.faces[3]]
    vehicle_faces = body.faces[6:]

    if not body:
        print("Error: Imported design contains no solid bodies. Exiting.")
        return

    # 4. Create Named Selection 1: Whole Body Selection
    # Select the entire body for a simulation part
    design.create_named_selection("inlet",faces=inlet)
    design.create_named_selection("outlet",faces=outlet)
    design.create_named_selection("vehicle",faces=vehicle_faces)
    print("Named selections created successfully.")

    # 5. Export the Design with Named Selections
    design.export_to_pmdb()

    print("\nScript finished successfully.")


if __name__ == "__main__":
    # Ensure this script is executed in an environment where the Ansys Geometry service 
    # (e.g., SpaceClaim or Discovery) is running or can be launched.
    run_geometry_script()
