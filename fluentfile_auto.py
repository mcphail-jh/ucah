from pathlib import Path
import os
import time
import logging
import json

# Import the core components from the PyAnsys library
from ansys.geometry.core import launch_modeler_with_spaceclaim
from ansys.geometry.core.misc.options import ImportOptions
import ansys.fluent.core as pyfluent


class CFD_job:
    def __init__(self, case_folder, ansys_version=251, nprocs=8):
        
        self.case_folder = case_folder
        self.ansys_version = ansys_version
        # number of processors to use
        self.nprocs = nprocs

    def _mesh_geometry(self, cad_path : str):
        '''
        Creates the named selections for a CAD file and returns/saves a mesh object to `self.case_folder`
        '''

        CAD_FILE_PATH = cad_path

        # 1. Initialize the Geometry Service (Connects to SpaceClaim/Discovery backend)
        # launch geometry
        print("Launching Geometry Service...")
        model = launch_modeler_with_spaceclaim()

        try:
            print("Geometry Service launched successfully.")

            # 2. Import the CAD File
            print(f"Importing CAD file: {CAD_FILE_PATH}...")
            
            # This function returns the active Design object containing all geometry.
            # Using a dummy file path if the real one isn't found to let the script proceed
            # in a non-execution environment, but will warn the user.
            if os.path.exists(CAD_FILE_PATH):
                design = model.open_file(file_path=CAD_FILE_PATH, upload_to_server=False, import_options=ImportOptions())
                print("CAD file imported successfully.")
            else:
                raise FileNotFoundError(f"Could not import CAD file at {CAD_FILE_PATH}. Check your path and try again.")

            # 3. Access the Imported Geometry
            body = design.bodies[0]

            # identify name surface regions
            
            inlet = []
            outlet = []
            vehicle_faces = []
            for face in body.faces:
                # bounding box is 5 x 5 x 2.5m, so those should be the only faces with area greater than 12m^2
                if face.area.magnitude > 12.0:
                    # assumes nose of missile is facing negative x
                    if (face.normal().x == 1):
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
            geo_file = design.export_to_pmdb(self.case_folder)
        
        finally:
            # regardless of if an error occurs or not, close SpaceClaim
            model.close()
        
        # Launch Fluent in meshing mode
        print("Launching Fluent Meshing...")
        # IMPORTANT to ensure fluent log and mesh files save in the case folder
        os.chdir(self.case_folder)
        mesher = pyfluent.launch_fluent(ui_mode="gui",
                                        mode="meshing", 
                                        processor_count=self.nprocs,
                                        dimension=pyfluent.Dimension.THREE,
                                        precision=pyfluent.Precision.DOUBLE)
        
        # run the mesh journal to do the actual meshing on the named selection geometry
        print("Meshing...")
        self._mesh_journal(mesher, geo_file._str)

        # VOLUME MESH IS NOW SAVED TO TaskObject11.msh.h5 in a subfolder

        return mesher
    
    def _mesh_journal(self, mesher, geo_file_path):
        '''
        Runs the steps to mesh the geometry with the named selections file saved at `geo_file_path`
        '''
        workflow = mesher.workflow
        workflow.InitializeWorkflow(WorkflowType=r'Watertight Geometry')
        tasks = workflow.TaskObject
        import_geometry = tasks['Import Geometry']
        import_geometry.Arguments.set_state({r'FileName': geo_file_path, r'ImportCadPreferences': {r'MaxFacetLength': 0,}, r'LengthUnit': r'm'})
        mesher.workflow.TaskObject['Import Geometry'].Execute()

        mesher.workflow.TaskObject['Add Local Sizing'].Arguments.set_state({r'AddChild': r'yes',r'BOICellsPerGap': 1,r'BOIControlName': r'vehicle_size',r'BOICurvatureNormalAngle': 18,r'BOIExecution': r'Face Size',r'BOIFaceLabelList': [r'vehicle'],r'BOIGrowthRate': 1.15,r'BOISize': 0.0025,r'BOIZoneorLabel': r'label',})
        mesher.workflow.TaskObject['Add Local Sizing'].AddChildAndUpdate(DeferUpdate=False)
        mesher.workflow.TaskObject['Add Local Sizing'].Execute()
        mesher.workflow.TaskObject['Generate the Surface Mesh'].Arguments.set_state({r'CFDSurfaceMeshControls': {r'CellsPerGap': 1,r'CurvatureNormalAngle': 14,r'MaxSize': 0.3,r'MinSize': 0.002,},})
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

    def _solver_journal(self, solver):
        # density based solver

        # energy on
        # viscous: SST k-omega
        # Materials -> air
        # density: ideal gas
        # Viscosity: sutherland
        # Materials -> solid
        # Granta MDS Database -> Titanium Ti6Al-4V Cast (grade 5)

        # Boundary conditions
        # Inlet
        # pressure-farfield
        # 0 Pa operating condition
        # Gauge pressure 100 Pa
        # Mach 5
        # Set components of velocity for given AOA
        # Thermal -> sea level temp or set temp to altitude

        # Outlet
        # Pressure outlet
        # Gauge pressure: 10 Pa
        # Check components given AOA
        # Thermal -> sea level temp or set temp to altitude

        # Wall
        # Thermal -> Convection
        # Heat transfer coeff. 50 W/(m^2 K) for now
        # Freestream temp?
        # Wall thickness: 0?

        # Reference values -> compute from inlet

        # Controls
        # Courant number 0.09
        
        # Report Definitions
        # Lift force, drag force, thermal something

        # mesh adaption?


        pass


    def run_fluent(self, setup_file, mesh_file=None, cad_file=None, iter=1000):
        '''
        Run the case. Takes either a mesh file or CAD file (first calls mesh_geometry to mesh it)
        '''
        # if the path to a mesh file is given, start a fluent solver and load in the mesh
        if mesh_file is not None:
            solver = pyfluent.launch_fluent(mode=pyfluent.FluentMode.SOLVER, 
                                        processor_count=self.nprocs,
                                        dimension=pyfluent.Dimension.THREE,
                                        precision=pyfluent.Precision.DOUBLE)
            
            solver.file.read(file_type="case", file_name= mesh_file)
        
        # otherwise if a cad_file is given, mesh it first then switch to solver mode
        elif cad_file is not None:
            mesher = self._mesh_geometry(cad_file)
            #mesher.tui.file.write_mesh(path=os.path.join(self.case_folder, "mesh.msh.h5"))
            solver = mesher.switch_to_solver()
        else:
            raise Exception("A mesh file or CAD file must be specified!")

        # Call solver journal function to setup case (WIP)
        self._solver_journal(solver)

        # Initialize and run
        solver.settings.solution.initialization.hybrid_initialize()
        solver.settings.solution.run_calculation.iterate(iter_count=iter)
        solver.settings.file.write_case_data(file_name="Output.cas.h5")

        solver.exit()

        # TODO: figure out format for results file
        # read each rfile.out file and collect the last value to put into a output.json
        output_json = {}
        for f in os.listdir(self.case_folder):
            if f.endswith('rfile.out'):
                full_path = os.path.join(self.case_folder, f)
                with open(full_path) as file:
                    lines = file.readlines()
                    report_name = lines[1].strip().split()[1].strip('\"')
                    last_line = lines[-1]
                    num_iter, last_value = last_line.strip().split()
                    last_value = float(last_value)
                    output_json[report_name] = last_value
        
        # write json to the case folder
        json_path = os.path.join(self.case_folder, 'output.json')
        with open(json_path, 'w') as file:
            json.dump(output_json, file)
        print("results saved to output.json")
        

if __name__ == "__main__":

    '''
    path = os.path.join(os.getcwd(),"parametric_v4_box.STEP")
    case = CFD_job(cad_path=path,ansys_version=251)
    case.run_geometry()
    case.run_fluent()
    '''

