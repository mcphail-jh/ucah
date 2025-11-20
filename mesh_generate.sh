#!/bin/bash

###################################################################
csv_file="mesh_folder/Case_Info_Template_V2.csv" # name of your CSV file
csv_mesh_folder="mesh_folder"       # mesh file
base_journal="basejournal.jou" # template journal file
base_dir="/scratch/qvu2hx/case"  # main directory for all cases
###################################################################

mesh_csv_dir=${base_dir}/${csv_mesh_folder}
mesh_lst=("${mesh_csv_dir}"/*.msh.h5)

mkdir -p "$base_dir"
counter=0


tail -n +3 "$csv_file" | while IFS=',' read -r case_name mach alpha beta fx fy fz temp density pressure viscosity sos velocity; do
    
    # Remove potential spaces
    case_name=$(echo "$case_name" | xargs)
    dir="${base_dir}/${case_name}"
    mkdir -p "$dir"

    # Copy mesh
    cp "${mesh_lst[$counter]}" "$dir/"
    
    counter=$counter+1

    # --- Create journal file ---
    jou_file="${dir}/${case_name}.jou"
    sed -e "s/__M__/${mach}/g" \
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
	





