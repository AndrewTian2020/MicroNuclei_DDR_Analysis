#!/usr/bin/bash
# Post Processing Scripts for Micronuclei ML Pipeline
# Aug 10, 2025
# Author: Andrew Tian
#
# This script takes the .json outputs from the ML pipeline and
# writes all of the important data onto excel spreadsheets.
# 
# Usage: ./post_processing.sh <base_directory> <json_directory>

# Function to display usage information
usage() {
    echo "Usage: $0 <base_directory> <json_directory>"
    echo "  <base_directory>: Path to the base directory containing input data"
    echo "  <json_directory>: Path to the directory contaning .json files"
    exit 1
}

# Check if base directory is provided
if [ $# -lt 2 ]; then
    echo "Error: Base directory and json directory not provided"
    usage
fi

# Define the base directories
BASE_DIR="$1"
# Define the json directory, which is a subfolder of the base directory containing .json files
jp="$2"

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Base directory '$BASE_DIR' does not exist or is not accessible"
    usage
fi

# Check if json directory exists
if [ ! -d "$BASE_DIR/$jp" ]; then
    echo "Error: Json directory '$BASE_DIR/$jp' does not exist or is not accessible"
    usage
fi

# Create log directory
LOG_DIR="${BASE_DIR}/pipeline_logs"
mkdir -p $LOG_DIR
LOG_FILE="${LOG_DIR}/pipeline_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a $LOG_FILE
}

log "Starting Post Processing Pipeline"
log "======================================="

INPUT_DIR="${BASE_DIR}/${jp}"
OUTPUT_DIR="${BASE_DIR}/${jp}-excels"

log "Processing ${jp} for splitting"
log "Input directory: ${INPUT_DIR}"
log "Output directory: ${OUTPUT_DIR}"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if output directory is empty
if [ -z "$(ls -A "$OUTPUT_DIR")" ]; then
    # Submit the splitting job
    JOB_ID=$(sbatch excel_writer.sh "$INPUT_DIR" "$OUTPUT_DIR")
    
    log "Submitted split job for ${wp} (Job ID: ${JOB_ID})"
else
    log "Output directory ${OUTPUT_DIR} is not empty. Skipping split job."
fi

log "Post processing completed"
