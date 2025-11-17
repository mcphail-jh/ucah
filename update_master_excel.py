'''
Simple script to create an excel sheet with all the cases in a given database folder.
Shows name, input parameters, output values (if applicable), and status (Not Done, Locked, Done)
'''

import pandas as pd
import os
import json
from datetime import datetime
from generate_input_json import *
from generate_output_json import *

def update_cases(root_dir):
    '''
    Walks through each subfolder in `root_dir`, attempts to generate the input and output JSOn files, then reads them into a master dataframe.

    Returns a dataframe with the updated values from each case/subfolder in the root folder.
    '''
    all_data = [] # List to store dictionaries (each dict will be a row)

    # Use os.walk to iterate through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip the root directory itself if it doesn't contain the data structure
        if dirpath == root_dir:
            continue

        case_name = os.path.basename(dirpath)

        # attempt to generate input and output json files. If there is an issue, skip the case and print a warning message
        try:
            generate_input_json(dirpath)
            generate_output_json(dirpath)
        except:
            print(f"Could not generate JSON for case {case_name}. Skipping.")
            continue
        
        # Determine the expected JSON filename (e.g., "Case_1.json")
        json_filename = f"{case_name}.json"
        json_file_path = os.path.join(dirpath, json_filename)
        
        # Check if the primary JSON file exists
        if not os.path.exists(json_file_path):
            # print(f"Skipping folder {folder_name}: {json_filename} not found.")
            continue
        
        # IGNORING STATUS since rivanna cases are only uploaded after they are done
        '''
        # Initialize the status variable
        status = "Output JSON Missing"
        
        
        # --- Determine Status and handle output.json ---
        output_file_path = os.path.join(dirpath, 'output.json')
        lock_file_path = os.path.join(dirpath, 'lock.txt')
        
        if os.path.exists(output_file_path):
            status = "Done"
        elif os.path.exists(lock_file_path):
            status = "Locked"
        '''

        # --- Load data ---
        with open(json_file_path, 'r') as f:
            row_data = json.load(f)
        
        # If output.json exists, also load its data into the row
        output_file_path = os.path.join(dirpath, 'output.json')
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as f:
                output_data = json.load(f)
                row_data.update(output_data) # Merge output data

        all_data.append(row_data)

        #row_data['Status'] = status # Finally, add the determined status

    # Create the final DataFrame
    df = pd.DataFrame(all_data)
    print(f"Updated dataframe with {len(all_data)} cases")
    return df

def write_master_excel(df : pd.DataFrame, save_dir : str, filename="Master.xlsx"):
    '''
    Saves the df as an excel file inside `save_dir`. Adds a column for a timestamp and converts the df cells to an excel table.
    '''
    save_path = os.path.join(save_dir, filename)

    df = df.fillna('')
    # add column for timestamp
    now = datetime.now()
    formatted_time = now.strftime(r'%b %d %Y, %I:%M%p')
    # only populate the first row with the timestamp
    df['Last Updated'] = [formatted_time] + ['' for i in range(df.shape[0]-1)]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(save_path, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object. Turn off the default
    # header and index and skip one row to allow us to insert a user defined
    # header.
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = []
    for header in df.columns:
        column_settings.append({'header': header})

    # Add the table.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
    print(f"Updated worksheet saved to {filename}")


def choose_folder_via_dialog():
    '''
    Function to select a folder in the file dialog if no arguments are passed
    '''
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title='Select project folder')
        root.destroy()
        return folder
    except Exception as e:
        print('Error opening folder dialog:', e, file=sys.stderr)
        return ''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', nargs='?')
    args = parser.parse_args()

    if args.folder is None:
        folder = choose_folder_via_dialog()
    else:
        folder = args.folder

    # get dataframe with updated cases and fill nan values with empty strings
    df = update_cases(folder)
    write_master_excel(df, folder)
