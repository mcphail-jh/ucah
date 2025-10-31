import ansys.fluent.core as pyfluent
import os
import numpy as np

wd = os.path.join(os.getcwd(),"first test")
solver_session = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=5,cwd=wd)
mesh_path = os.path.join(wd,"Winged_Missile_2024.msh.h5")
solver_session.file.read_case(file_name = mesh_path)


def solver_setup_journal(solver_session,AoA,mach,iter):
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

    flow_x = np.cos(AoA)
    flow_z = np.sin(AoA)

    pressure_farfield = solver_session.setup.boundary_conditions.pressure_far_field[
        "inlet"
    ]
    pressure_farfield.momentum.gauge_pressure = 100
    pressure_farfield.momentum.mach_number = mach
    pressure_farfield.thermal.temperature = 288.15
    pressure_farfield.momentum.flow_direction[0] = flow_x
    pressure_farfield.momentum.flow_direction[2] = flow_z
    pressure_farfield.turbulence.turbulent_intensity = 0.05
    pressure_farfield.turbulence.turbulent_viscosity_ratio = 10

    pressure_outlet = solver_session.setup.boundary_conditions.pressure_outlet["outlet"]

    pressure_outlet.momentum.gauge_pressure = 10
    pressure_outlet.momentum.backflow_dir_spec_method = "Direction Vector"

    wall_cond = solver_session.setup.boundary_conditions.wall["vehicle"]

    wall_cond.thermal.thermal_condition = "Convection"
    wall_cond.thermal.heat_transfer_coeff = 50
    wall_cond.thermal.free_stream_temp = 288.15

    ref_vals = solver_session.setup.reference_values.zone = "inlet"

    sol = solver_session.solution
    report = sol.report_definitions

    # report definitions

    def create_report_file(solver_session,rep_name):
        file_rep = solver_session.solution.monitor.report_files
        file_rep[rep_name+"-rfile"] = {}
        file_obj = file_rep[rep_name+"-rfile"]
        file_obj.report_defs.set_state(rep_name)

        
    # rad heat flux
    report.flux['rad_heat'] = {}
    rad_ht = report.flux['rad_heat']
    rad_ht.report_type.set_state("flux-radheattransfer")
    rad_ht.boundaries.set_state("vehicle")
    create_report_file(solver_session,"rad_heat")

    # tot heat flux 
    report.flux['tot_heat'] = {}
    tot_ht = report.flux['tot_heat']
    tot_ht.report_type.set_state("flux-heattransfer")
    tot_ht.boundaries.set_state("vehicle")
    create_report_file(solver_session,"tot_heat")

    # lift force 
    report.lift['lift_force'] = {}
    lft = report.lift['lift_force']
    lft.report_output_type.set_state("Lift Force")
    lft.zones.set_state("vehicle")
    create_report_file(solver_session,"lift_force")

    # lift coeff
    report.lift['lift_coeff'] = {}
    lft = report.lift['lift_coeff']
    lft.report_output_type.set_state("Lift Coefficient")
    lft.zones.set_state("vehicle")
    create_report_file(solver_session,"lift_coeff")

    # drag force 
    report.drag['drag_force'] = {}
    lft = report.drag['drag_force']
    lft.report_output_type.set_state("Drag Force")
    lft.zones.set_state("vehicle")
    create_report_file(solver_session,"drag_force")

    # drag coeff
    report.drag['drag_coeff'] = {}
    lft = report.drag['drag_coeff']
    lft.report_output_type.set_state("Drag Coefficient")
    lft.zones.set_state("vehicle")
    create_report_file(solver_session,"drag_coeff")
    input()
    sol.controls.courant_number = .09
    # 
    session = solver_session
    session.settings.solution.run_calculation.iter_count = 5
    session.settings.solution.initialization.hybrid_initialize()
    session.settings.solution.run_calculation.iterate(iter_count=iter)
    


if __name__ == "__main__":
    AoA = 5 # degrees
    mach = 5
    Iter = 5
    solver_setup_journal(solver_session,AoA,mach,Iter)