# ================================================================================
# Date: June 19, 2025
# Written By: Andrew Tian
# Script to take .json files and input the data onto excel
# Also automated so that other users can directly input data

import json
import os
from mn_data_interpreter import jsonFile
import xlsxwriter
from pathvalidate import is_valid_filename

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
    # Initializing variables
    valid_folder = False
    new_sheet = True
    new_folder = True
    excel_name = ""
    sheet_name = ""

    sheet_list = []

    input_dir = ""

    continue_sheet = ""

    # Check for valid excel name
    excel_name = str(input("Please insert the name of the excel you want (must be valid excel filename): "))
    print("\n")
    while is_valid_filename(excel_name) == False:
        print("ERROR: Make sure your excel filename is a valid filename. Try again.")
        excel_name = str(input("Please insert the name of the excel you want (must be valid excel filename): "))
        print("\n")
    excel_name = excel_name + ".xlsx"
    workbook = xlsxwriter.Workbook(excel_name)
    
    # Keep adding new sheets until the user wants to quit
    while new_sheet == True:
        valid_folder = False
        new_folder = True

        # Check for valid sheetname
        sheet_name = str(input("Please insert the name of the sheet (must be <32 chars long), can't be same name as before: "))
        print("\n")
        while len(sheet_name) > 32 or is_valid_filename(sheet_name) == False or sheet_name in sheet_list:
            if len(sheet_name) > 32:
                print("Error: sheet name must be less than 32 characters long.")
                sheet_name = str(input("Please insert the name of the sheet (must be <32 chars long): "))
                print("\n")
            elif sheet_name in sheet_list:
                print("Error: sheet name can't be a previous sheet.")
                sheet_name = str(input("Please insert the name of the sheet (must be <32 chars long): "))
                print("\n")
            else:
                print("Error: sheet name must be valid, only numbers, letters, and underscores (no spaces, can't start with a number). Try again")
                sheet_name = str(input("Please insert the name of the sheet (must be <32 chars long): "))
                print("\n")
        sheet_list.append(sheet_name)

        # Check for valid pathway to folder containing .json files
        while new_folder == True:
            input_dir = str(input("Please input the directory to the folder containing all .jsons (or type 'cancel' to cancel): "))
            while valid_folder == False and input_dir != "cancel":
                try:
                    os.listdir(input_dir)
                    valid_folder = True
                except:
                    print("\n")
                    print("Invalid file input. Please try again.")
                    input_dir = str(input("Please insert the json file directory (or type 'cancel' to cancel): "))
            if valid_folder == True:
                worksheet = workbook.add_worksheet(sheet_name)
                write_folder(input_dir = input_dir, sheet = worksheet, apop_thresh = 5, dist_thresh = 50)
                valid_folder = False
                new_folder = False
            if input_dir == "cancel":
                new_folder = False
                sheet_list.remove(sheet_name)
        
        # Auto-fit the sheet to the text width
        worksheet.autofit()
        
        # Check if user wants to add a new sheet
        while continue_sheet != "Y" and continue_sheet != "N":
            continue_sheet = str(input("New sheet? Y/N: "))
            if continue_sheet == "Y":
                new_sheet = True
                new_folder = True
            elif continue_sheet == "N":
                new_sheet = False
            else:
                print("Invalid input. Please input Y/N.")
        continue_sheet = ""
    workbook.close()
    print("Thanks!")

#if __name__ == "__main__":
#    main()

# ================================================================================
# ADDITIONAL TESTING
workbook = xlsxwriter.Workbook("NP-20250625-MCF10AGFPH2BCAS9-cellcycleval-2.xlsx")
worksheet1 = workbook.add_worksheet("IR")
worksheet2 = workbook.add_worksheet("NIR")
write_folder("/Volumes/Lexar/Nupur_Jsons/NP-20250625-MCF10AGFPH2BCAS9-cellcycleval-2-IR-json", worksheet1, 2, 25)
write_folder("/Volumes/Lexar/Nupur_Jsons/NP-20250625-MCF10AGFPH2BCAS9-cellcycleval-2-NIR-json", worksheet2, 2, 25)
workbook.close()