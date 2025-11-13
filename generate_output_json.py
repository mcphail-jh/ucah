'''
Function to manually create an output json file 
(useful if the case failed or you want to pull results from a manually-ran case)

Pulls the last value from all rfiles in `case_folder`
'''
import os, json, sys

def generate_output_json(case_folder):
    # read each rfile.out file and collect the last value to put into a output.json
    output_json = {}
    for f in os.listdir(case_folder):
        if f.endswith('.out') and not f.endswith("1_1.out"):
            full_path = os.path.join(case_folder, f)
            with open(full_path) as file:
                lines = file.readlines()
                report_name = lines[1].strip().split()[1].strip('\"')
                last_line = lines[-1]
                num_iter, last_value = last_line.strip().split()
                last_value = float(last_value)
                output_json[report_name] = last_value
                output_json['Iterations'] = num_iter
    
    # write json to the case folder
    json_path = os.path.join(case_folder, 'output.json')
    with open(json_path, 'w') as file:
        json.dump(output_json, file)
    print("results saved to output.json")


if __name__ == "__main__":
    folder = ' '.join(sys.argv[1::])
    if sys.argv[1] == '-r':
        top_level_folder = ' '.join(sys.argv[2::])
        if not os.path.isdir(top_level_folder):
            print("Error! Please enter a valid folder path!")
        else:
            for subfolder in os.listdir(top_level_folder):
                full_path = os.path.join(top_level_folder, subfolder)
                generate_output_json(full_path)
 
    else: # if -r is not specified, generate output json for this one folder
        if not os.path.isdir(folder):
            print("Error! Please enter a valid folder path!")
        else:
            generate_output_json(folder)
        