import ansys.fluent.core as pyfluent

solver = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=8)

solver.tui.file.read_mesh(path=r"C:\Users\qvu2hx\ucah\first test\Winged_Missile_2024.msh.h5")
