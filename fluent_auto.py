import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

import_file_name = examples.download_file('mixing_elbow.pmdb', 'pyfluent/mixing_elbow')
print(f"Importing geometry from: {import_file_name}")
"""
meshing_session = pyfluent.launch_fluent(
    mode=pyfluent.FluentMode.MESHING, precision=pyfluent.Precision.DOUBLE, processor_count=2
)
watertight = meshing_session.watertight()
watertight.import_geometry.file_name.set_state(import_file_name)
watertight.import_geometry.length_unit.set_state('in')
watertight.import_geometry()
"""