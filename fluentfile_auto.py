import ansys.fluent.core as pyfluent
import os

working_directory = r"C:\auto_files"

geometry_file = "Winged_Missile_2024.IGS"
meshing_file =  "FFF.msh.h5"
orig_geo = "FFF.agdb"
setup_file = "setup.cas.h5"
results_file = "new_results.cas.h5"


# defining full paths
new_geometry_file = os.path.join(working_directory,geometry_file)
meshing_file = os.path.join(working_directory,meshing_file)
setup_file = os.path.join(working_directory,setup_file)
results_file = os.path.join(working_directory,results_file)
print("meshing file")
print(meshing_file)
# Launch Fluent in meshing mode
mesher = pyfluent.launch_fluent(mode="meshing",ui_mode=pyfluent.UIMode.GUI, processor_count=8)

# If you need to read an existing meshing case while in meshing mode,
# use the TUI file command available on the meshing session.
# The Meshing session object doesn't expose `file` like the solver session does,
# which caused the AttributeError you saw.
mesher.tui.file.read_mesh(meshing_file)

# Clear any existing zones/mesh data

mesher.tui.mesh.clear_mesh()
# Assuming your new geometry file is named 'new_geometry.stl'
new_geometry_file = os.path.join(working_directory,geometry_file)


# Read the new geometry into the mesher
mesher.workflow.TaskObject['Import Geometry'].Revert()
mesher.workflow.TaskObject['Import Geometry'].Arguments.set_state({r'FileName': r'C:/auto_files/Winged_Missile_2024.IGS',r'ImportCadPreferences': {r'MaxFacetLength': 0,},r'LengthUnit': r'm',r'NumParts': 1,})
mesher.workflow.TaskObject['Import Geometry'].Execute()

input()
# If using the Watertight Geometry workflow, often you need to update the
# boundary/region definitions after loading a new geometry:
mesher.tui.meshing.update_geometry_definitions()

# Assuming a standard Watertight Geometry workflow:

# 1. Update boundary names if they changed (Crucial if face names in CAD changed)
# You may need TUI commands here to re-map boundary condition types to new face names.

# 2. Generate the surface mesh
mesher.tui.meshing.mesh.generate_surface_mesh()

# 3. Generate the volume mesh (e.g., polyhedral or hexcore)
mesher.tui.meshing.mesh.generate_volume_mesh()

# Switch the session to the solver context
solver = mesher.switch_to_solver()

# Read only the setup from the case file, keeping the mesh you just created
solver.file.read_case(file_name=setup_file, read_data=False, read_mesh=False)

# Initialize and run
solver.solution.initialization.hybrid_initialize()
solver.solution.run_calculation.iterate(number_of_iterations=100)

# Save the final result
solver.file.write_case_data(file_name=results_file)
solver.exit()

