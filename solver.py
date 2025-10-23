import ansys.fluent.core as pyfluent
from ansys.fluent.core import solver as fluent_solver
import os



def mesh_case(case_folder, save_file=True):
    '''
    Run the "meshing_journal.py" journal file to create and return a mesh object from the IGS file in `case_folder`. If `save_file` is specified, it will save the mesh as a file.
    '''

    # Get path to the IGS file getting meshed
    file_path = None
    for f in os.lisdir(case_folder):
        if f.endswith('.igs'):
            file_path = os.path.join(case_folder, f)

    if file_path is None:
        print("No IGS file found in ", case_folder)
        return

    # Launch Fluent in meshing mode
    meshing_session = pyfluent.launch_fluent(mode="meshing")


    # Import the meshing journal file
    # The journal file (meshing_journal.py) must be edited to use the 'file_path' variable
    # for importing the geometry.
    try:
        meshing_session.file.read_journal(journal_file_name="meshing_journal.py")

        # TODO: Add logic to get mesh object and return it and save file if specified. Also error handling.
    except Exception as e:
        print(f"Meshing failed with exception: {e}\nClosing session.")
        meshing_session.exit()


    return meshing_session




'''
Given a pyfluent mesh object (either passed by another python script or loaded in from a .msh file) and a local case folder, run the solution and save the results
'''
def solve_case(mesh_object, case_folder):



    # Get the file name without the extension for creating a unique output file
    file_name = 'output'



    # -------------- BELOW CODE FROM GEMINI - NEED TO REVIEW -----------------------------
    # --- Environment setup and session launch (for demonstration) ---
    # Replace 'your_mesh_file.msh.h5' with your actual mesh file.
    # In your automation script, this would be part of the loop.
    solver = pyfluent.launch_fluent(mode="solver")
    solver.file.read_case(file_name="your_mesh_file.msh.h5")
    # ----------------------------------------------------------------

    # Sea-level temperature constant in Kelvin (approximate)
    # You can set this to a more precise value or derive it from the units library if needed
    sea_level_temp_k = 288.15 

    # --- General Setup ---
    # Density based solver
    solver.setup.general.solver.type = "density-based-explicit" # or "density-based-implicit"

    # --- Models ---
    # Energy: On
    solver.setup.models.energy.enabled = True

    # Viscous: SST k-omega
    solver.setup.models.viscous.model = "k-omega"
    solver.setup.models.viscous.k_omega_model = "sst"

    # --- Materials ---
    # Air (as a fluid)
    air_material = solver.setup.materials.fluid["air"]
    # Density: ideal gas
    air_material.density.option = "ideal-gas"
    # Viscosity: Sutherland
    air_material.viscosity.option = "sutherland"
    # You can customize the Sutherland coefficients if needed, but defaults are often fine for air
    # air_material.viscosity.sutherland.reference_temperature = 273.11 # K
    # air_material.viscosity.sutherland.reference_viscosity = 1.716e-05 # kg/(m s)
    # air_material.viscosity.sutherland.effective_temperature = 110.56 # K

    # Solid: Titanium Grade 5 from database
    # First, you need to copy the material from the database.
    # The exact name needs to be confirmed from the database. This is the likely name.
    titanium_name = "titanium, alpha-beta alloy, ti-6al-4v, cast, hip, annealed (grade 5)"
    solver.setup.materials.database.copy_by_name(
        type="solid", 
        name=titanium_name
    )

    # --- Boundary Conditions ---
    # Operating Conditions (set before boundary conditions)
    solver.setup.boundary_conditions.operating_conditions.operating_pressure = 0

    # Inlet (Pressure Far-Field)
    # Replace 'inlet' with the correct boundary zone name from your mesh
    solver.setup.boundary_conditions.pressure_far_field["inlet"].gauge_pressure = 100
    solver.setup.boundary_conditions.pressure_far_field["inlet"].mach_number = 5
    solver.setup.boundary_conditions.pressure_far_field["inlet"].thermal.temperature = sea_level_temp_k

    # Outlet (Pressure Outlet)
    # Replace 'outlet' with the correct boundary zone name
    solver.setup.boundary_conditions.pressure_outlet["outlet"].gauge_pressure = 10
    solver.setup.boundary_conditions.pressure_outlet["outlet"].thermal.temperature = sea_level_temp_k

    # Wall (Convection)
    # Replace 'wall' with the correct boundary zone name
    # Set the wall thickness to 0
    solver.setup.boundary_conditions.wall["wall"].thermal.thermal_bc = "convection"
    solver.setup.boundary_conditions.wall["wall"].thermal.convection.heat_transfer_coefficient = 50
    solver.setup.boundary_conditions.wall["wall"].thermal.convection.freestream_temperature = sea_level_temp_k
    solver.setup.boundary_conditions.wall["wall"].thermal.wall_thickness = 0

    # --- Reference Values ---
    solver.solution.initialization.reference_values.compute_from = "inlet"
    # Note: You can't directly use "compute from inlet" for a density-based solver.
    # A better approach is to set the values manually after computing from the inlet to have control.
    # If you run `solver.solution.initialization.reference_values.compute_from = "inlet"`,
    # it will update the other fields, which you can then read and potentially modify.
    # For example:
    # solver.solution.initialization.reference_values.area = 0.5 * wetted_area

    # --- Controls ---
    solver.solution.controls.pseudo_time_method.courant_number = 0.09

    # --- Report Definitions ---
    # Replace 'wall' with the actual boundary zone for your missile.
    # Replace 'ref_area' with the correct reference area.
    ref_area = 1.0 # This needs to be calculated from your geometry
    ref_length = 1.0 # Set a relevant reference length
    # Create report definition for Lift
    solver.solution.report_definitions.force.create(
        name="lift", 
        type="lift", 
        direction=[0, 1, 0], # Assuming lift is in the y-direction
        surfaces=["wall"],
        options={"report_to_console": True, "print": True, "plot": True}
    )
    # Create report definition for Drag
    solver.solution.report_definitions.force.create(
        name="drag", 
        type="drag", 
        direction=[1, 0, 0], # Assuming drag is in the x-direction
        surfaces=["wall"],
        options={"report_to_console": True, "print": True, "plot": True}
    )

    # --- Initialization ---
    solver.solution.initialization.hybrid_initialize()

    # --- Calculation ---
    # You can set the number of iterations
    solver.solution.run_calculation.iterate(number_of_iterations=1000)

    # You can save the project or case/data files
    solver.file.write_case(file_name="solved_case.cas.h5")
    solver.file.write_data(file_name="solved_data.dat.h5")

    # Close the session
    solver.exit()
