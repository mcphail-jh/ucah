# Import the core components from the PyAnsys library
from ansys.geometry.core import launch_modeler_with_spaceclaim
from ansys.geometry.core.misc.options import ImportOptions
import ansys.fluent.core as pyfluent

import os
from fluentfile_auto import CFD_job


tot_case_folder = "C:/folder"


case_lst = os.listdir(tot_case_folder)

for case in case_lst:
    case_folder = case
    case_obj = CFD_job(case_folder)
    cad_path = [f for f in os.listdir(case) if f.lower().endswith(".step")][0]
    case_obj._mesh_geometry(str(cad_path))

