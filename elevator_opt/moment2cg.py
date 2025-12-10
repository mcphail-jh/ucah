import numpy as np
import pandas as pd
import sys

cg = np.array([.48952, -.01224])


def choose_folder_via_dialog():
    '''
    Function to select a folder in the file dialog if no arguments are passed
    '''
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file = filedialog.askopenfilename(title='Select project file')
        root.destroy()
        return file
    except Exception as e:
        print('Error opening folder dialog:', e, file=sys.stderr)
        return ''


file = "C:/Users/Soren Poole/OneDrive - University of Virginia/Capstone/elevator_opt/elevator_aoa_results/Master.xlsx"
param_file = "C:/Users/Soren Poole/OneDrive - University of Virginia/Capstone/elevator_opt/elevator_cases/CAD/elevator_cases_design_table2.xlsx"  
#file = choose_folder_via_dialog()
data = pd.read_excel(file)
lift = data['lift_force']
drag = data['drag_force']
moment = data['moment']
aoa = data['aoa-deg']

params = pd.read_excel(param_file)


moment_cg = np.zeros(len(lift))

for i in range(len(lift)):
    l = lift[i]
    m = moment[i]
    aoa_i = aoa[i]
    F = np.array([-l*np.sin(np.radians(aoa_i)), l*np.cos(np.radians(aoa_i))])
    moment_cg[i] = m - np.cross(cg,F)

thing = data['moment']
data["cg moment"] = moment_cg
print(moment_cg)

ele_angle = np.zeros(len(data['Name']))
ch_length = np.zeros(len(data['Name']))
case_name = []
param_name_lst = params.values[:,0].tolist()
for i in range(len(data['Name'])):
    case_num = param_name_lst.index(data['Name'][i])
    ele_angle[i] = params['$VALUE@CS_Angle@EQUATIONS'][case_num]
    ch_length[i] = params['$VALUE@Wing_CS_Depth@EQUATIONS'][case_num]
    case_name.append(data['Name'][i])



output_dict = {
    'case': case_name,
    'aoa': aoa,
    'ele_angle': ele_angle,
    'ch_length': ch_length,
    'cl': lift,
    'cd': drag,
    'cm': moment_cg,
}
df = pd.DataFrame(output_dict)

df.to_csv("krig_file3.csv",index=False)