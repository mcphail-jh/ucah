'''
Given a NON-SYMMETRICAL 3D CAD file (.step, .STEP) or named-selection geometry file (.pmdb), this script creates a mesh file as specified in `mesh_journal()`

To run, call python mesh.py [cad_file_path]. If the file is ran with no filepath argument, a window will pop up to manually select the file.

'''
from ansys.geometry.core import launch_modeler_with_spaceclaim
from ansys.geometry.core.misc.options import ImportOptions
import ansys.fluent.core as pyfluent
import os, sys

NUM_PROCS = 16

def name_selections_symmetrical(cad_path):
    cad_file_name = os.path.basename(cad_path)
    folder = os.path.dirname(cad_path)
    # launch geometry
    print("Launching Geometry Service...")
    model = launch_modeler_with_spaceclaim()
    
    try:
        print("Geometry Service launched successfully.")

        # 2. Import the CAD File
        print(f"Importing CAD file: {cad_file_name}...")
        
        # This function returns the active Design object containing all geometry.
        # Using a dummy file path if the real one isn't found to let the script proceed
        # in a non-execution environment, but will warn the user.
        if os.path.exists(cad_path):
            design = model.open_file(file_path=cad_path, upload_to_server=False, import_options=ImportOptions())
            print("CAD file imported successfully.")
        else:
            raise FileNotFoundError(f"Could not import CAD file at {cad_path}. Check your path and try again.")

        # 3. Access the Imported Geometry
        body = design.bodies[0]

        # identify name surface regions
        inlet = []
        outlet = []
        vehicle_faces = []
        symmetry = []
        for face in body.faces:
            # bounding box is 5 x 5 x 2.5m, so those should be the only faces with area greater than 12m^2
            if face.area.magnitude > 12.0:
                # assumes nose of missile is facing negative x
                if (face.normal().x == 1):
                    outlet.append(face)
                elif (face.normal().y == -1):
                    symmetry.append(face)
                else:
                    inlet.append(face)
            else:
                vehicle_faces.append(face)

        if not body:
            raise Exception("Error: Imported design contains no solid bodies.")

        # 4. Create Named Selection 1: Whole Body Selection
        # Select the entire body for a simulation part
        design.create_named_selection("inlet",faces=inlet)
        design.create_named_selection("outlet",faces=outlet)
        design.create_named_selection("vehicle",faces=vehicle_faces)
        design.create_named_selection("symmetry",faces=symmetry)
        print("Named selections created successfully.")

        # 5. Export the Design with Named Selections
        named_selections_path = str(design.export_to_pmdb(folder))

        return named_selections_path
    
    finally:
        # regardless of if an error occurs or not, close SpaceClaim
        model.close()


def name_selections(cad_path):
    cad_file_name = os.path.basename(cad_path)
    folder = os.path.dirname(cad_path)
    # launch geometry
    print("Launching Geometry Service...")
    model = launch_modeler_with_spaceclaim()
    
    try:
        print("Geometry Service launched successfully.")

        # 2. Import the CAD File
        print(f"Importing CAD file: {cad_file_name}...")
        
        # This function returns the active Design object containing all geometry.
        # Using a dummy file path if the real one isn't found to let the script proceed
        # in a non-execution environment, but will warn the user.
        if os.path.exists(cad_path):
            design = model.open_file(file_path=cad_path, upload_to_server=False, import_options=ImportOptions())
            print("CAD file imported successfully.")
        else:
            raise FileNotFoundError(f"Could not import CAD file at {cad_path}. Check your path and try again.")

        # 3. Access the Imported Geometry
        body = design.bodies[0]

        # identify name surface regions
        inlet = []
        outlet = []
        vehicle_faces = []
        for face in body.faces:
            # bounding box is 5 x 5 x 5m, so those should be the only faces with area greater than 24m^2
            if face.area.magnitude > 24.0:
                # assumes nose of missile is facing POSITIVE x
                if (face.normal().x == -1):
                    outlet.append(face)
                else:
                    inlet.append(face)
            else:
                vehicle_faces.append(face)

        if not body:
            raise Exception("Error: Imported design contains no solid bodies.")

        # 4. Create Named Selection 1: Whole Body Selection
        # Select the entire body for a simulation part
        design.create_named_selection("inlet",faces=inlet)
        design.create_named_selection("outlet",faces=outlet)
        design.create_named_selection("vehicle",faces=vehicle_faces)
        print("Named selections created successfully.")

        # 5. Export the Design with Named Selections
        named_selections_path = str(design.export_to_pmdb(folder))

        return named_selections_path
    
    finally:
        # regardless of if an error occurs or not, close SpaceClaim
        model.close()
        

def mesh(named_selections_path):
    '''
    Takes a named-selection geometry file (.pmdb) and creates a mesh according to the settings specified below. 
    
    This function contains the python journal file responsible for the actual meshing.
    '''
    folder = os.path.dirname(named_selections_path)

    # Launch Fluent in meshing mode
    print("Launching Fluent Meshing...")

    # IMPORTANT to ensure fluent log and mesh files save in the case folder
    os.chdir(folder)

    mesher = pyfluent.launch_fluent(ui_mode="gui",
                                    mode="meshing", 
                                    processor_count=NUM_PROCS,
                                    dimension=pyfluent.Dimension.THREE,
                                    precision=pyfluent.Precision.DOUBLE)
    
    # run the mesh journal to do the actual meshing on the named selection geometry
    print("Meshing...")
    mesh_journal(mesher, named_selections_path)
    print("Mesh file saved in", folder)
    # mesh is now saved in the same folder as the CAD and named selections files
    # close the fluent connection and return
    mesher.exit()


def mesh_journal(mesher, named_selections_path):
    '''
    Given a fluent meshing session, execute the commands to create the desired mesh.
    '''
    #TODO: Add constants here to make changing common settings easier

    workflow = mesher.workflow
    workflow.InitializeWorkflow(WorkflowType=r'Watertight Geometry')
    tasks = workflow.TaskObject
    import_geometry = tasks['Import Geometry']
    import_geometry.Arguments.set_state({r'FileName': named_selections_path, r'ImportCadPreferences': {r'MaxFacetLength': 0,}, r'LengthUnit': r'm'})
    mesher.workflow.TaskObject['Import Geometry'].Execute()

    mesher.workflow.TaskObject['Add Local Sizing'].Arguments.set_state({r'AddChild': r'yes',r'BOICellsPerGap': 1,r'BOIControlName': r'vehicle_size',r'BOICurvatureNormalAngle': 18,r'BOIExecution': r'Face Size',r'BOIFaceLabelList': [r'vehicle'],r'BOIGrowthRate': 1.15,r'BOISize': 0.0025,r'BOIZoneorLabel': r'label',})
    mesher.workflow.TaskObject['Add Local Sizing'].AddChildAndUpdate(DeferUpdate=False)
    mesher.workflow.TaskObject['Add Local Sizing'].Execute()
    mesher.workflow.TaskObject['Generate the Surface Mesh'].Arguments.set_state({r'CFDSurfaceMeshControls': {r'CellsPerGap': 1,r'CurvatureNormalAngle': 8,r'MaxSize': 0.3,r'MinSize': 0.002,},})
    mesher.workflow.TaskObject['Generate the Surface Mesh'].Execute()
    mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=False)
    mesher.workflow.TaskObject['Describe Geometry'].Arguments.set_state({r'NonConformal': r'No',r'SetupType': r'The geometry consists of only fluid regions with no voids',})
    mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=True)
    mesher.workflow.TaskObject['Describe Geometry'].Execute()
    mesher.workflow.TaskObject['Update Boundaries'].Arguments.set_state({r'BoundaryLabelList': [r'inlet'],r'BoundaryLabelTypeList': [r'pressure-far-field'],r'OldBoundaryLabelList': [r'inlet'],r'OldBoundaryLabelTypeList': [r'velocity-inlet'],})
    mesher.workflow.TaskObject['Update Boundaries'].Execute()
    mesher.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(Arguments={r'v1': True,}, SetupTypeChanged=False)
    # line below throwing error "invalid argument [1] improper list" as of 10/24
    #mesher.workflow.TaskObject['Update Regions'].Arguments.set_state({r'OldRegionNameList': [r'fluid'],r'OldRegionTypeList': [r'fluid'],r'RegionNameList': [r'fluid'],r'RegionTypeList': [r'dead'],})
    mesher.workflow.TaskObject['Update Regions'].Execute()
    mesher.workflow.TaskObject['Add Boundary Layers'].Arguments.set_state({r'BLControlName': r'last-ratio_1',r'BlLabelList': [r'vehicle'],r'FaceScope': {r'GrowOn': r'selected-labels',},r'FirstHeight': 2e-05,r'LocalPrismPreferences': {r'Continuous': r'Continuous',},r'NumberOfLayers': 20,r'OffsetMethodType': r'last-ratio',r'TransitionRatio': 0.2,})
    mesher.workflow.TaskObject['Add Boundary Layers'].AddChildAndUpdate(DeferUpdate=False)
    mesher.workflow.TaskObject['Generate the Volume Mesh'].Arguments.set_state({r'PrismPreferences': {r'ShowPrismPreferences': False,},r'VolumeFill': r'polyhedra',r'VolumeFillControls': {r'GrowthRate': 1.15,},r'VolumeMeshPreferences': {r'ShowVolumeMeshPreferences': True,},})
    mesher.workflow.TaskObject['Generate the Volume Mesh'].Arguments.set_state({r'PrismPreferences': {r'ShowPrismPreferences': False,},r'VolumeFill': r'polyhedra',r'VolumeFillControls': {r'GrowthRate': 1.15,r'TetPolyMaxCellLength': 0.5,},r'VolumeMeshPreferences': {r'ShowVolumeMeshPreferences': False,},})
    mesher.workflow.TaskObject['Generate the Volume Mesh'].Execute()
    mesher.tui.file.write_mesh()

def choose_file_via_dialog():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file = filedialog.askopenfilename(title='Select Geometry File')
        root.destroy()
        return file
    except Exception as e:
        print('Error opening folder dialog:', e, file=sys.stderr)
        return ''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()

    if args.filename is None:
        file_path = choose_file_via_dialog()
    else:
        file_path = args.filename

    if file_path.lower().endswith(".step"):
        named_selections_path = name_selections(file_path)
        mesh(named_selections_path)
    elif file_path.lower().endswith(".pmdb"):
        mesh(file_path)
    else:
        print(f"Invalid file: {file_path}. Please choose a .step CAD file or .pmdb named-selections file.")
    