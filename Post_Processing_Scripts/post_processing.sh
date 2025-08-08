#!/usr/bin/bash
# Post Processing Scripts for Micronuclei ML Pipeline
# July 9, 2025
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
# Define the work directory, which is a subdirectory of the base directory
jp="$2"

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Base directory '$BASE_DIR' does not exist or is not accessible"
    usage
fi

# Check if work directory exists
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

# Function to wait for jobs to complete
wait_for_jobs() {
    local job_ids=("$@")
    log "Waiting for ${#job_ids[@]} jobs to complete..."
    
    # Wait for all jobs to complete
    for job_id in "${job_ids[@]}"; do
        while squeue -j "$job_id" | grep -q "$job_id"; do
            log "Job $job_id is still running. Waiting..."
            sleep 60  # Check every minute
        done
        log "Job $job_id has completed."
    done
    
    log "All jobs have completed."
}

log "Starting Post Processing Pipeline"
log "======================================="

# Write Excel sheet containing all the .jsons
log ""
log "---------------------------------------------------"
# Array to store job IDs
split_job_ids=()

