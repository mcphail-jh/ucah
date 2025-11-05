'''
Simple script to create an excel sheet with all the cases in a given database folder.
Shows name, input parameters, output values (if applicable), and status (Not Done, Locked, Done)
'''

import pandas as pd
import os
import json
from datetime import datetime

def update_cases_in_excel(root_dir):
    all_data = [] # List to store dictionaries (each dict will be a row)

    # Use os.walk to iterate through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip the root directory itself if it doesn't contain the data structure
        if dirpath == root_dir:
            continue
        
        folder_name = os.path.basename(dirpath)
        
        # Determine the expected JSON filename (e.g., "FolderA.json")
        json_filename = f"{folder_name}.json"
        json_file_path = os.path.join(dirpath, json_filename)
        
        # Check if the primary JSON file exists
        if not os.path.exists(json_file_path):
            # print(f"Skipping folder {folder_name}: {json_filename} not found.")
            continue
            
        # Initialize the status variable
        status = "Not Done"
        
        # --- Determine Status and handle output.json ---
        output_file_path = os.path.join(dirpath, 'output.json')
        lock_file_path = os.path.join(dirpath, 'lock.txt')

        if os.path.exists(output_file_path):
            status = "Done"
        elif os.path.exists(lock_file_path):
            status = "Locked"
        
        # --- Load data ---
        with open(json_file_path, 'r') as f:
            row_data = json.load(f)
        
        row_data['Status'] = status # Add the determined status
        
        # If output.json exists, also load its data into the row
        if status == "Done":
            with open(output_file_path, 'r') as f:
                output_data = json.load(f)
                row_data.update(output_data) # Merge output data

        all_data.append(row_data)

    # Create the final DataFrame
    df = pd.DataFrame(all_data)
    print(f"Updated dataframe with {len(all_data)} rows")
    return df


if __name__ == "__main__":
    SHEET_NAME = "Master_Update.xlsx"
    DB_NAME = "Database"
    remote_folder = os.path.expanduser("~\\OneDrive - University of Virginia\\UCAH Hypersonic Design Competition Capstone Group - Documents\\" + DB_NAME)
    save_path = os.path.join(remote_folder, SHEET_NAME)
    # below line is used for local testing
    #save_path = os.path.expanduser("~\\Downloads\\Master_Update.xlsx")

    # get dataframe with updated cases and fill nan values with empty strings
    df = update_cases_in_excel(remote_folder)
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
    print(f"Updated worksheet saved to {SHEET_NAME}")

    #df.to_excel(save_path, index=False)