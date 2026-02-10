#!/bin/bash

# IMPORTANT
# If you want to transfer everything (DAT and dat) include #nocaseglob

dest_folder="elevator_aoa_results"
case_folder="elevator_aoa_cases"
# Make the main transfer directory
mkdir -p transfer
for case_dir in ${case_folder}/Case_*; do
    if [ -d "$case_dir" ]; then
        case_name=$(basename "$case_dir")
        
        mkdir -p "transfer/$case_name"

        jou_file="$case_dir/${case_name}.jou"
        if [ -f "$jou_file" ]; then
            cp "$jou_file" "transfer/$case_name/"
        fi

	if [ -f "${case_dir}/*.json" ]; then
		cp "${case_dir}/*.json" "transfer/$case_name"
	fi

        shopt -s nullglob #nocaseglob
        for dat_file in "$case_dir"/dat*; do
            cp "$dat_file" "transfer/$case_name/"
        done
        shopt -u nullglob # nocaseglob
	
        if [ -f "$case_dir/heat_t.out" ]; then
            cp "$case_dir/heat_t.out" "transfer/$case_name/"
        fi

        echo "Processed $case_name"
    fi
done
mv "./transfer" "./${dest_folder}"

echo "Done. Files are in ./${dest_folder}/"

