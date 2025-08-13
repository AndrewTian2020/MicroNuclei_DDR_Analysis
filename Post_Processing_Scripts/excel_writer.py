# ================================================================================
# Date: June 19, 2025
# Written By: Andrew Tian
# Script to take .json files and input the data onto excel
# Also automated so that other users can directly input data

import os
import argparse
from mn_data_interpreter import jsonFile
import xlsxwriter

# Write on the new file
def write_sheet(item, sheet, column, apop_thresh = 2, dist_thresh = 25):
    i = 1
    n = 0
    
    # Sort the .json and write column titles
    item.sort_alpha()

    # Filter jsonFile object based on thresholds
    item.apop_threshold(apop_thresh)

    # ============= REMINDER TO SELF ===================
    # EDIT/CHANGE THE DISTANCE FILTER THRESHOLD FOR ULISES
    # DATASETS UNTIL AN OPTIMAL DISTANCE IS FOUND
    item.dist_threshold(dist_thresh)

    sheet.write(0, column, "Image ID")
    sheet.write(0, column + 1, "Nuclei")
    sheet.write(0, column + 2, "Micronuclei")
    sheet.write(0, column + 3, "MN Ratio")
    n = len(item.image_ids)

    # Write all .json info into cells
    for row, name in enumerate(item.image_ids):
        sheet.write(row + 1, column, name)
        print("Writing: " + str(name) + " " + str(i) + "/" + str(n))
        i += 1
    for row, name in enumerate(item.nuclei_counts):
        sheet.write(row + 1, column + 1, name)
    for row, name in enumerate(item.micronuclei_counts):
        sheet.write(row + 1, column + 2, name)
    for row, name in enumerate(item.mn_ratios):
        sheet.write(row + 1, column + 3, name)

# Inputs all the .json files of a folder into a singular excel sheet
def write_folder(input_dir, sheet, apop_thresh = 2, dist_thresh = 25.0):
    files = os.listdir(input_dir)
    files.sort()
    
    col = 0

    for file in files:
        try:
            write_sheet(jsonFile(str(input_dir) + "/" + str(file)), sheet, col, apop_thresh = apop_thresh, dist_thresh = dist_thresh)
            col += 5
            print("Wrote: " + str(file))
            print("\n")
        except:
            print("ERROR: Could not write: " + str(file))
            print("May be an invalid .json or invalid file.")
            print("\n")

def main():
    """Main function to parse arguments and run the partitioning"""
    parser = argparse.ArgumentParser(
        description='Run post-processing and write .json outputs onto excel'
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Source directory containing image files'
    )
    
    parser.add_argument(
        '--destination', '-d',
        required=True,
        help='Destination directory for excel file'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    if not os.path.isdir(args.source):
        print(f"Error: Source directory '{args.source}' does not exist")
        return
    else:
        # Start writing sheets
        workbook = xlsxwriter.Workbook(str(args.destination) + "/Output.xlsx")
        worksheet1 = workbook.add_worksheet("Data")
        write_folder(args.source, worksheet1, 2, 25)
        worksheet1.autofit()
        workbook.close()

if __name__ == "__main__":
    main()