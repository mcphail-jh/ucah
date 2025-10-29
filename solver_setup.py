import ansys.fluent.core as pyfluent
import os

wd = os.path.join(os.getcwd(),"first test")
solver_session = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=5,cwd=wd)
mesh_path = os.path.join(wd,"Winged_Missile_2024.msh.h5")
solver_session.file.read_case(file_name = mesh_path)

# model : k-omega
# k-omega model : sst

viscous = solver_session.setup.models.viscous

viscous.model = "k-omega"
viscous.k_omega_model = "sst"

# density : ideal-gas
# viscosity : sutherland
# viscosity method : three-coefficient-method
# reference viscosity : 1.716e-05 [kg/(m s)]
# reference temperature : 273.11 [K]
# effective temperature : 110.56 [K]

air = solver_session.setup.materials.fluid["air"]

air.density.option = "ideal-gas"
input()