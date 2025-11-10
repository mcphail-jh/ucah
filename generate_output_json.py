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
        if f.endswith('rfile.out'):
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
    folder = sys.argv[1]

    if not os.path.isdir(folder):
        print("Error! Please enter a valid folder path!")
    else:
        generate_output_json(folder)
    