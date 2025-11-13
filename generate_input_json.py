'''
Function to manually create an input json file 
(useful if you're importing manual cases or cases from rivanna which don't have an input json file)

Pulls the 'define' values from the journal files in `case_folder`
'''
import os, json, sys

def generate_input_json(case_folder):
    # read each rfile.out file and collect the last value to put into a output.json
    folder_name = os.path.basename(case_folder)
    input_json = {"Name": folder_name}

    for f in os.listdir(case_folder):
        if f.endswith('.jou'):
            full_path = os.path.join(case_folder, f)
            with open(full_path) as file:
                # hard-coded behavior based on format of .jou files as of 11/13/25
                lines = file.readlines()
                # index of the first line with input variables
                line_index = 3
                while lines[line_index].startswith("(define"):
                    # expecting format '(define variable numbervalue)
                    line_values = lines[line_index].split()
                    variable_name = line_values[1]
                    # cut the closed parentheses from the value
                    value = float(line_values[2][:-1])
                    # add to the json file
                    input_json[variable_name] = value
                    # increment the line
                    line_index += 1
    
    # write json to the case folder
    json_path = os.path.join(case_folder, f'{folder_name}.json')
    with open(json_path, 'w') as file:
        json.dump(input_json, file)
    print(f"results saved to {folder_name}.json")


if __name__ == "__main__":
    folder = ' '.join(sys.argv[1::])
    if sys.argv[1] == '-r':
        top_level_folder = ' '.join(sys.argv[2::])
        if not os.path.isdir(top_level_folder):
            print("Error! Please enter a valid folder path!")
        else:
            for subfolder in os.listdir(top_level_folder):
                full_path = os.path.join(top_level_folder, subfolder)
                generate_input_json(full_path)
 
    else: # if -r is not specified, generate input json for this one folder
        if not os.path.isdir(folder):
            print("Error! Please enter a valid folder path!")
        else:
            generate_input_json(folder)
        