import os
from pathlib import Path
import time

# Import the core components from the PyAnsys Geometry library
from ansys.geometry.core.connection import launcher as launch
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.math import Plane
print(dir(Modeler))
# --- Configuration ---

# NOTE: Replace this with the actual path to your CAD file (e.g., .step, .x_t, .iges)
CAD_FILE_PATH = Path("C:/CAD_Models/engine_mount.step")
EXPORT_DESIGN_NAME = "design_with_selections"

def run_geometry_script():
    """
    Connects to the Geometry service, imports a CAD file, and creates named selections.
    """
    if not CAD_FILE_PATH.exists():
        print(f"ERROR: CAD file not found at path: {CAD_FILE_PATH}")
        print("Please update 'CAD_FILE_PATH' to a valid .step, .iges, or other supported file.")
        # We can't proceed without a file, so we'll mock the import for demonstration
        # In a real scenario, you would raise an error or exit here.
        # For this script, we'll connect but skip the core logic if the file is missing.
        # return

    # 1. Initialize the Geometry Service (Connects to SpaceClaim/Discovery backend)
    #print(f"Service connection successful. Modeler initialized in {modeler.units.name} units.")
    input()

    # launch geometry
    model = launch.launch_modeler_with_spaceclaim()
    design = model.create_design()
    print(dir(design))
  
    try:
        # 2. Import the CAD File
        print(f"Importing CAD file: {CAD_FILE_PATH.name}...")
        
        # This function returns the active Design object containing all geometry.
        # Using a dummy file path if the real one isn't found to let the script proceed
        # in a non-execution environment, but will warn the user.
        if CAD_FILE_PATH.exists():
            design = Modeler.import_design(CAD_FILE_PATH)
        else:
            # Mocking a basic design object for code demonstration purposes
            # (In a live environment, this block would not be needed)
            print("WARNING: Skipping actual file import due to missing file. Using a mock design object.")
            return # Exit since we cannot mock selection reliably

        # 3. Access the Imported Geometry
        bodies = design.bodies

        if not bodies:
            print("Error: Imported design contains no solid bodies. Exiting.")
            return

        # We will select the first body in the design
        main_body = bodies[0]
        print(f"Found {len(bodies)} bodies. Targeting the first body: {main_body.name}")

        # 4. Create Named Selection 1: Whole Body Selection
        # Select the entire body for a simulation part
        body_selection = Selection(elements=[main_body])
        ns_body_name = "SIM_PART_MAIN_COMPONENT"
        modeler.create_named_selection(ns_body_name, body_selection)
        print(f"Created Named Selection: '{ns_body_name}' (Targeting 1 Body)")


        # 5. Create Named Selection 2: Specific Face Selection
        # Select a specific face for boundary conditions (e.g., fixed support)
        if main_body.faces:
            selected_face = main_body.faces[0] # Selecting the first face found on the body
            face_selection = Selection(elements=[selected_face])
            ns_face_name = "BC_FIXED_SUPPORT_FACE"
            modeler.create_named_selection(ns_face_name, face_selection)
            print(f"Created Named Selection: '{ns_face_name}' (Targeting 1 Face)")
        else:
             print("Warning: Could not create face selection as no faces were found on the main body.")


        # 6. Verification and Export (Optional)
        print("\n--- Verification ---")
        all_ns = modeler.get_named_selections()
        print(f"Total Named Selections in Design: {len(all_ns)}")
        for ns in all_ns:
            print(f"- {ns.name}: Contains {len(ns.elements)} elements.")

        # Export the modified design back out (e.g., as a SpaceClaim file with NS)
        export_path = Path(CAD_FILE_PATH.parent) / f"{EXPORT_DESIGN_NAME}.scdoc"
        print(f"\nExporting design with Named Selections to: {export_path}")
        modeler.export_design(design, export_path)

        print("\nScript finished successfully.")

    except Exception as e:
        print(f"An error occurred during the process: {e}")

    finally:
        # 7. Clean up and close the service connection
        print("Closing the Geometry Service connection.")
        service.close()


if __name__ == "__main__":
    # Ensure this script is executed in an environment where the Ansys Geometry service 
    # (e.g., SpaceClaim or Discovery) is running or can be launched.
    run_geometry_script()
