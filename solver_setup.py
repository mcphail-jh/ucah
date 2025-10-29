import ansys.fluent.core as pyfluent
import os

wd = os.path.join(os.getcwd(),"first test")
solver_session = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=5,cwd=wd)
mesh_path = os.path.join(wd,"Winged_Missile_2024.msh.h5")
solver_session.file.read_case(file_name = mesh_path)

solver_session.setup.general.solver.type = "density-based-implicit"

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

# Boundary conditions for inlet - pressure far field
# gauge pressure : 0 [Pa]
# mach number : 0.8395
# temperature : 255.56 [K]
# x-component of flow direction : 0.998574
# z-component of flow direction : 0.053382
# turbulent intensity : 5 [%]
# turbulent viscosity ratio : 10



pressure_farfield = solver_session.setup.boundary_conditions.pressure_far_field[
    "inlet"
]
pressure_farfield.momentum.gauge_pressure = 100
pressure_farfield.momentum.mach_number = 5
pressure_farfield.thermal.temperature = 288.15
pressure_farfield.momentum.flow_direction[0] = .996194698092
pressure_farfield.momentum.flow_direction[2] = 0.0871557427477
pressure_farfield.turbulence.turbulent_intensity = 0.05
pressure_farfield.turbulence.turbulent_viscosity_ratio = 10

pressure_outlet = solver_session.setup.boundary_conditions.pressure_outlet["outlet"]

pressure_outlet.momentum.gauge_pressure = 10
pressure_outlet.momentum.backflow_dir_spec_method = "Direction Vector"

wall_cond = solver_session.setup.boundary_conditions.wall["vehicle"]

wall_cond.thermal.thermal_condition = "Convection"
print(vars(wall_cond.thermal))
wall_cond.thermal.heat_transfer_coeff = 50
wall_cond.thermal.free_stream_temp = 288.15

sol = solver_session.solution
report = sol.report_definitions
print(vars(report))
report.flux.create(name="rad_heat")
report.flux.create(name="tot_heat")


# not correct (reporting zone empty)
report.flux._objects["rad_heat"] = {"zones": ["vehicle"]}
print(vars(report.flux))





input()
