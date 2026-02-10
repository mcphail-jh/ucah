#!/bin/bash

###################################################################
csv_file="Case_Info_Jan_elevator.csv" # name of your CSV file
csv_mesh_folder="elevator_mesh"       # mesh file
base_journal="symJournalFVD.jou" # template journal file
base_dir="/scratch/qvu2hx/case"  # main directory for all cases
case_folder="Jan_elevator_cases" # folder where current cases are running
###################################################################

mesh_csv_dir="${base_dir}/${csv_mesh_folder}"
mesh_lst=("${mesh_csv_dir}"/*)
case_path="${base_dir}/${case_folder}"

mkdir -p "$base_dir"
counter=0


tail -n +3 "$csv_file" | while IFS=',' read -r case_name mach alpha beta fx fy fz temp density pressure viscosity sos velocity; do

    # Remove potential spaces
    case_name=$(echo "$case_name" | xargs)
    mesh_path="${mesh_lst[$counter]}"
    mesh_name="${mesh_path##*/}"

    dir="${base_dir}/${case_folder}/${case_name}"
    mkdir -p "$dir"

    # Copy mesh
    cp "${mesh_path}" "$dir/"

    if [ -e "${case_path}/*.json" ]; then
            cp "${case_path}"/*.json "$dir/"
    fi

    (( counter++ ))

    # --- Create journal file ---
    jou_file="${dir}/${case_name}.jou"
    sed -e "s/__MESH__/${mesh_name}/g" \
        -e "s/__M__/${mach}/g" \
        -e "s/__AOA__/${alpha}/g" \
        -e "s/__B__/${beta}/g" \
        -e "s/__FX__/${fx}/g" \
        -e "s/__FY__/${fy}/g" \
        -e "s/__FZ__/${fz}/g" \
        -e "s/__T__/${temp}/g" \
        -e "s/__D__/${density}/g" \
        -e "s/__P__/${pressure}/g" \
        -e "s/__VIS__/${viscosity}/g" \
        -e "s/__SOS__/${sos}/g" \
        -e "s/__V__/${velocity}/g" \
        "$base_journal" > "$jou_file"

    # --- Create Slurm run script ---
    slurm_file="${dir}/${case_name}.sh"
    cat > "$slurm_file" <<EOF
#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --ntasks=40
#SBATCH --time=15:00:00
#SBATCH --account=xinfeng_gao
#SBATCH --partition=standard
#SBATCH -o outjob.out
#SBATCH -e errjob.err

module load gcc openmpi
module load ansys/2024r2

cd "${dir}"
fluent 3ddp -i ${case_name}.jou -g -t \$SLURM_NTASKS -cflush
EOF
        echo "${case_name}"
done


# rm_char script
for f in /scratch/qvu2hx/case/${case_folder}/Case_*/Ca*.jou; do
    tr -d '\r' < "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
    echo "Cleaned $f"
done


# go script to submit jobs
# Loop through all case directories
for dir in ${case_folder}/*; do
    echo ${dir}
    if [[ -d "$dir" ]]; then
        cd "$dir"

        slurm_file=$(ls *.sh 2>/dev/null | head -n1)

        if [[ -n "$slurm_file" ]]; then
            echo "Submitting $slurm_file in $dir"
            sbatch "$slurm_file"
        else
            echo "No .slurm file found in $dir, skipping."
        fi

        cd ../..
    fi
done
                                               
