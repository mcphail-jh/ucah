import ansys.fluent.core as pyfluent
import os
import numpy as np



def solver_setup_journal(solver_session : pyfluent.Solver, AoA=5, mach=5):
    solver_session.settings.setup.general.solver.type = "density-based-implicit"

    # model : k-omega
    # k-omega model : sst

    viscous = solver_session.settings.setup.models.viscous

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

    flow_x = np.cos(np.deg2rad(AoA))
    flow_z = np.sin(np.deg2rad(AoA))


    pressure_farfield = solver_session.setup.boundary_conditions.pressure_far_field[
        "inlet"
    ]
    pressure_farfield.momentum.gauge_pressure = 530
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

    ref = solver_session.setup.reference_values
    ref.area = .15 # should be 0.015
    ref.density = .001209025
    ref.enthalpy = 1736426
    ref.length = 1
    ref.pressure = 100
    ref.temperature = 288.15
    ref.velocity = 1700.837
    ref.viscosity = .00001789532

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
    lft.force_vector.set_state([0,0,1])
    create_report_file(solver_session,"lift_force")

    # lift coeff
    report.lift['lift_coeff'] = {}
    lft = report.lift['lift_coeff']
    lft.report_output_type.set_state("Lift Coefficient")
    lft.zones.set_state("vehicle")
    lft.force_vector.set_state([0,0,1])
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
    
    # 11/3 increased from 0.09
    sol.controls.courant_number = .15

    # enable compressibility effects and corner flow correction
    solver_session.execute_tui(r"/define/models/viscous/turb-compressibility? yes")
    solver_session.execute_tui(r"/define/models/viscous/corner-flow-correction? yes")


    # mesh adaption
    '''
    apt = solver_session.mesh.adapt.set
    apt.adaption_method = 'puma'
    dyn = apt.dynamic_adaption()
    dyn.enable = True
    apt.dynamic_adaption_frequency = 100
    '''

    # add a new mesh adaption with pressure based hessian
    #criteria = solver_session.tui.mesh.adapt.predefined_criteria.aerodynamics.error_based.pressure_hessian_indicator
    #solver_session.tui.mesh.adapt.manage_criteria.add(criteria)

    '''
    solver_session.settings.solution.run_calculation.iter_count = 5
    solver_session.settings.solution.initialization.hybrid_initialize()
    solver_session.settings.solution.run_calculation.iterate(iter_count=iter)
    '''


if __name__ == "__main__":
    wd = os.path.join(os.getcwd())
    solver_session = pyfluent.launch_fluent(mode="solver",ui_mode=pyfluent.UIMode.GUI, processor_count=5,cwd=wd)
    mesh_path = os.path.join(wd,"Winged_Missile_2024.msh.h5")
    solver_session.file.read_case(file_name = mesh_path)

    AoA = 5 # degrees
    mach = 5
    iter = 5
    solver_setup_journal(solver_session, AoA, mach, iter)
