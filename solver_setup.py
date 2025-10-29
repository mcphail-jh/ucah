import ansys.fluent.core as pyfluent
import os

wd = os.path.join(os.getcwd(),"first test")
solver = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=5,cwd=wd)
solver.tui.file.read_mesh(path=os.path.join(wd,"Winged_Missile_2024.msh.h5"))