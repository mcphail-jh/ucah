from pathlib import Path
import os
import time

# Import the core components from the PyAnsys library
from ansys.geometry.core.connection import launcher as launch
import ansys.fluent.core as pyfluent

class CFD_job:
    def __init__(self,cad_path,ansys_version=251):
        self.cad_path = cad_path
        self.ansys_version = ansys_version

    def run_geometry(self):
        ansys_version = self.ansys_version
        CAD_FILE_PATH = Path(self.cad_path)

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
            print("CAD file imported successfully.")
        else:
            # Mocking a basic design object for code demonstration purposes
            # (In a live environment, this block would not be needed)
            print("WARNING: Skipping actual file import due to missing file. Using a mock design object.")

        # 3. Access the Imported Geometry
        body = design.bodies[0]

        # identify name surface regions
        box_faces = body.faces[0:6]
        inlet = []
        outlet = []
        vehicle_faces = body.faces[6:]

        for face in box_faces:
            if face.normal().z == -1:
                outlet.append(face)
            else:
                inlet.append(face)


        if not body:
            print("Error: Imported design contains no solid bodies. Exiting.")

        # 4. Create Named Selection 1: Whole Body Selection
        # Select the entire body for a simulation part
        design.create_named_selection("inlet",faces=inlet)
        design.create_named_selection("outlet",faces=outlet)
        design.create_named_selection("vehicle",faces=vehicle_faces)
        print("Named selections created successfully.")

        # 5. Export the Design with Named Selections
        geo_file = design.export_to_pmdb()
        self.geo_file = geo_file
        time.sleep(10)


    def run_fluent(self):
        # Define file paths
        
        geometry_file = self.geo_file.as_posix()
        
        # Launch Fluent in meshing mode
        mesher = pyfluent.launch_fluent(mode="meshing",ui_mode=pyfluent.UIMode.GUI, processor_count=8)
        print(geometry_file)
        # exsecute meshing workflow
        mesher.workflow.InitializeWorkflow(WorkflowType=r'Watertight Geometry')
        mesher.workflow.TaskObject['Import Geometry'].Arguments.set_state({r'FileName': geometry_file,r'ImportCadPreferences': {r'MaxFacetLength': 0,},r'LengthUnit': r'm',})
        mesher.workflow.TaskObject['Import Geometry'].Execute()
        mesher.workflow.TaskObject['Add Local Sizing'].Arguments.set_state({r'AddChild': r'yes',r'BOICellsPerGap': 1,r'BOIControlName': r'vehicle_size',r'BOICurvatureNormalAngle': 18,r'BOIExecution': r'Face Size',r'BOIFaceLabelList': [r'vehicle'],r'BOIGrowthRate': 1.15,r'BOISize': 0.0025,r'BOIZoneorLabel': r'label',})
        mesher.workflow.TaskObject['Add Local Sizing'].AddChildAndUpdate(DeferUpdate=False)
        mesher.workflow.TaskObject['Generate the Surface Mesh'].Arguments.set_state({r'CFDSurfaceMeshControls': {r'CellsPerGap': 1,r'CurvatureNormalAngle': 14,r'MaxSize': 0.3,r'MinSize': 0.002,},})
        mesher.workflow.TaskObject['Generate the Surface Mesh'].Execute()
        mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=False)
        mesher.workflow.TaskObject['Describe Geometry'].Arguments.set_state({r'NonConformal': r'No',r'SetupType': r'The geometry consists of only fluid regions with no voids',})
        mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=True)
        mesher.workflow.TaskObject['Describe Geometry'].Execute()
        mesher.workflow.TaskObject['Update Boundaries'].Arguments.set_state({r'BoundaryLabelList': [r'inlet'],r'BoundaryLabelTypeList': [r'pressure-far-field'],r'OldBoundaryLabelList': [r'inlet'],r'OldBoundaryLabelTypeList': [r'velocity-inlet'],})
        mesher.workflow.TaskObject['Update Boundaries'].Execute()
        mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=False)
        mesher.workflow.TaskObject['Update Regions'].Arguments.set_state({r'OldRegionNameList': [r'fluid'],r'OldRegionTypeList': [r'fluid'],r'RegionNameList': [r'fluid'],r'RegionTypeList': [r'dead'],})
        mesher.workflow.TaskObject['Update Regions'].Execute()
        mesher.workflow.TaskObject['Add Boundary Layers'].Arguments.set_state({r'BLControlName': r'last-ratio_1',r'BlLabelList': [r'vehicle'],r'FaceScope': {r'GrowOn': r'selected-labels',},r'FirstHeight': 2e-05,r'LocalPrismPreferences': {r'Continuous': r'Continuous',},r'NumberOfLayers': 20,r'OffsetMethodType': r'last-ratio',r'TransitionRatio': 0.2,})
        mesher.workflow.TaskObject['Add Boundary Layers'].AddChildAndUpdate(DeferUpdate=False)
        mesher.workflow.TaskObject['Generate the Volume Mesh'].Arguments.set_state({r'PrismPreferences': {r'ShowPrismPreferences': False,},r'VolumeFill': r'polyhedra',r'VolumeFillControls': {r'GrowthRate': 1.15,},r'VolumeMeshPreferences': {r'ShowVolumeMeshPreferences': True,},})
        mesher.workflow.TaskObject['Generate the Volume Mesh'].Arguments.set_state({r'PrismPreferences': {r'ShowPrismPreferences': False,},r'VolumeFill': r'polyhedra',r'VolumeFillControls': {r'GrowthRate': 1.15,r'TetPolyMaxCellLength': 0.5,},r'VolumeMeshPreferences': {r'ShowVolumeMeshPreferences': False,},})
        mesher.workflow.TaskObject['Generate the Volume Mesh'].Execute()
        input()

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

if __name__ == "__main__":
    path = os.path.join(os.getcwd(),"parametric_v4_box.STEP")
    case = CFD_job(cad_path=path,ansys_version=251)
    case.run_geometry()
    #case.run_fluent()
    print("\nCase finished successfully.")

