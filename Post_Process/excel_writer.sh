#!/bin/bash
#SBATCH --nodes=1
#SBATCH --mem=8G 
#SBATCH --time=12:00:00
#SBATCH --job-name=ExcelWrite
#SBATCH --output=%j-%x.out
#SBATCH --error=%j-%x.err

# Script to run post-processing and write MN info onto excel files
# Author: Andrew Tian
# Date: Aug 11, 2025

# Load required modules
module load python/3.11

# Create and activate virtual environment
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --upgrade pip

# Install required packages
pip install numpy==1.24.4
pip install xlsxwriter==3.2.3
pip install natsort==8.4.0
#pip install -r $HOME/Post_Process/requirements.txt

# Parameters
SOURCE_DIR=$1
DEST_DIR=$2

echo "Starting json writing"
echo "Source directory: $SOURCE_DIR"
echo "Destination directory: $DEST_DIR"

# Run the Python script
python $HOME/Post_Process/excel_writer.py --source "$SOURCE_DIR" --destination "$DEST_DIR"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "Successfully wrote jsons"
else
    echo "ERROR: Failed to write jsons"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo "Json writing completed"
