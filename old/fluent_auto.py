import ansys.fluent.core as pyfluent

import_file_name =  r"C:\Users\Soren Poole\OneDrive - University of Virginia\Capstone\Winged_Missile_2024.IGS"


meshing_session = pyfluent.launch_fluent(
    show_gui = True, mode=pyfluent.FluentMode.MESHING, precision=pyfluent.Precision.DOUBLE, processor_count=2
)

watertight = meshing_session.watertight()
watertight.import_geometry.file_name.set_state(import_file_name)
watertight.import_geometry.length_unit.set_state('in')
watertight.import_geometry()

# stops fluent from closing immediately
input()



