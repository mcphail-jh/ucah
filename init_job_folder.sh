#!/bin/bash

###################################################################
job_folder="Jan_elevator_cases" # folder where the cases, meshes, and journal files are located

###################################################################

base_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

job_folder_path="${base_dir}/${job_folder}"
mkdir -p "${job_folder_path}"

cp "${base_dir}/${job_folder}/mesh_combine_go.sh" "${job_folder_path}/"
cp "${base_dir}/${job_folder}/mesh_packup.sh" "${job_folder_path}/"

echo "Job folder initialized at: ${job_folder_path}"