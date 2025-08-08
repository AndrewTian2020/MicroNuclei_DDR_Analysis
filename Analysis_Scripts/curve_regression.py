# ===================================================================================================
# Date: July 11, 2025
# Author: Andrew Tian
# This code was made to analyze Kate's data.
# 
# It only does the curve regression and returns statistics related to that.
#
# All of the analysis data will be put onto an excel sheet.
# 
# A k-means clustering will then be used to group similar genes together based on their curve
# properties, although this will likely be done in a separate script.

# ===================================================================================================
# Extracting data from the excel sheet
from excel_reader import read_excel
from functions import derivate2

import xlsxwriter

import statistics
import numpy as np
from lmfit import Model
from lmfit import Parameters
import matplotlib.pyplot as plt

# ===================================================================================================
# PART 1: Curve regression

#loc_list_plate_1 = []
#scale_list_plate_1 = []
#msre_list_plate_1 = []

# Define functions to test out:

# FIX THIS FUNCTION LATER NOT SURE WHY ITS NOT WORKING
# INITIAL PARAMETERS: alpha = 1.7 (min = 0), beta = 60 (min = 0)
def weibull(x, alpha, beta):
    return alpha * (x**(alpha - 1)) / (beta ** alpha) * np.exp(-((x / beta)**(alpha)))

# INITIAL PARAMETERS: mu = 60, sig = 16
def gaussian(x, mu, sig):
    return 1.0 / (sig * np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * ((x - mu)/sig)**2.0)

# INITIAL PARAMETERS: mu = 3.5, sig = 0.6
def lognorm(x, mu, sig):
    return 1.0/(x * sig * np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * ((np.log(x) - mu)/sig)**2.0)

# INITIAL PARAMETERS: m = 0.001 (min = 0), b = 0 (min = 0)
def linear(x, m, b):
    return m * x + b

# INITIAL PARAMETERS: a = 0.025, c = 70
def sine(x, a, c):
    return a * np.sin(np.pi / 72 * (x - c)) + a

# INITIAL PARAMETERS: a = 0.025 (min = 0.0), b = 0.4 (min = 0.0), c = 3.0 (min = -3.0, max = 3.0), k = "a + delta" (set delta to be zero, min zero)
def customsin(x, a, b, c, k):
    return a * np.sin(x * np.pi / 72 - b + c * np.sin(x * np.pi / 72 - b)) + k

def extract_correlation(mn_list, n, t):
    # Scale x-axis to the time points
    x_data = []
    correlation = []
    for i in range(n + 1):
        x_data.append(i * t)
    x_data.remove(0)
    x_data = np.array(x_data)

    for mn in mn_list:
        msq = 0
        i = 0
        y_data = mn[:n]

        model = Model(customsin)
        params = Parameters()

        #customsin parameters
        params.add("a", value = 0.015, min = 0.0)
        params.add("b", value = 0.4)
        params.add("c", value = 3.0, min = -3.0, max = 3.0)
        params.add("delta", value = 0.0, min = 0.0)
        params.add("k", expr = "a + delta")

        result = model.fit(y_data, params, x = x_data)

        # Calculate mean square manually...
        while i < len(x_data):
            y1 = customsin(x_data[i], result.params["a"].value, result.params["b"].value, result.params["c"].value, result.params["k"].value)
            y2 = y_data[i]
            msq += (y1 - y2) ** 2
            i += 1
        msq /= i
        correlation.append(msq)

        #print(result.fit_report())
        #print(msq)
        #plt.plot(x_data, y_data, 'o')
        #plt.plot(x_data, result.init_fit, '--', label = 'initial fit')
        #plt.plot(x_data, result.best_fit, '-', label = 'best fit')
        #plt.legend()
        #plt.show()

    return correlation

# ===================================================================================================
# Writing correlation statistics to see which ones are the best

#rep_1_wells_p1, rep_1_wells_p2, rep_1_mn_p1, rep_1_mn_p2 = read_excel("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/excels (raw data)/20220719_Synthego_DDR_KO_library_rep_1.xlsx")
#rep_2_wells_p1, rep_2_wells_p2, rep_2_mn_p1, rep_2_mn_p2 = read_excel("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/excels (raw data)/20221107_Synthego_DDR_screen_rep_2.xlsx")

#rep_1_correl_p1 = extract_correlation(rep_1_mn_p1, 13, 12)
#rep_1_correl_p2 = extract_correlation(rep_1_mn_p2, 13, 12)
#rep_2_correl_p1 = extract_correlation(rep_2_mn_p1, 42, 3)
#rep_2_correl_p2 = extract_correlation(rep_2_mn_p2, 42, 3)

# Create a temporary sheet to list all chi square values
#workbook = xlsxwriter.Workbook("Cubic MSQ.xlsx")
#worksheet = workbook.add_worksheet("Data")
#worksheet.write(0, 0, "Rep 1 Plate 1 Well ID")
#worksheet.write(0, 1, "Correlation")
#worksheet.write(0, 3, "Rep 1 Plate 2 Well ID")
#worksheet.write(0, 4, "Correlation")
#worksheet.write(0, 6, "Rep 2 Plate 1 Well ID")
#worksheet.write(0, 7, "Correlation")
#worksheet.write(0, 9, "Rep 2 Plate 2 Well ID")
#worksheet.write(0, 10, "Correlation")

#for row, name in enumerate(rep_1_wells_p1):
#    worksheet.write(row + 1, 0, name)
#for row, name in enumerate(rep_1_correl_p1):
#    worksheet.write(row + 1, 1, name)
#for row, name in enumerate(rep_1_wells_p2):
#    worksheet.write(row + 1, 3, name)
#for row, name in enumerate(rep_1_correl_p2):
#    worksheet.write(row + 1, 4, name)
#for row, name in enumerate(rep_2_wells_p1):
#    worksheet.write(row + 1, 6, name)
#for row, name in enumerate(rep_2_correl_p1):
#    worksheet.write(row + 1, 7, name)
#for row, name in enumerate(rep_2_wells_p2):
#    worksheet.write(row + 1, 9, name)
#for row, name in enumerate(rep_2_correl_p2):
#    worksheet.write(row + 1, 10, name)

#worksheet.autofit()
#workbook.close()

# ===================================================================================================
# Extract all correlation statistics and areas
def calc_statistics(mn_list):
    xmaxes = []
    maxes = []
    correlation = []

    for mn in mn_list:
        msq = 0
        j = 0
        x_data = []
        n = len(mn)

        # Have to cut the rep 1 dataset in half
        if n == 26:
            n = 13
        y_data = mn[:n]

        # Initialize x range
        for i in range(n):
            x_data.append(144/(n - 1) * i)
        
        # Initialize model
        model = Model(customsin)
        params = Parameters()

        # Initialize customsin parameters
        params.add("a", value = 0.015, min = 0.0)
        params.add("b", value = 0.4, min = 0.0)
        params.add("c", value = 3.0, min = -3.0, max = 3.0)
        params.add("delta", value = 0.0, min = 0.0)
        params.add("k", expr = "a + delta")

        # Find curve of best fit and integrate the area
        result = model.fit(y_data, params, x = x_data)
        a = result.params["a"].value
        b = result.params["b"].value
        c = result.params["c"].value
        k = result.params["k"].value
        max = derivate2(a, b, c, k, 100)

        # Calculate mean square manually...
        while j < len(x_data):
            y1 = customsin(x_data[i], result.params["a"].value, result.params["b"].value, result.params["c"].value, result.params["k"].value)
            y2 = y_data[i]
            msq += (y1 - y2) ** 2
            j += 1
        msq /= j
        correlation.append(msq)
        xmaxes.append(max[0])
        maxes.append(max[1])

        #OPTIONAL: Display graphs (just comment them out if not using)
        #print(result.fit_report())
        #print("MAX: " + str(max))
        #plt.plot(x_data, y_data, 'o')
        #plt.plot(x_data, result.init_fit, '--', label = 'initial fit')
        #plt.plot(x_data, result.best_fit, '-', label = 'best fit')
        #plt.legend()
        #plt.show()

    return [xmaxes, maxes, correlation]

rep_1_wells_p1, rep_1_wells_p2, rep_1_mn_p1, rep_1_mn_p2 = read_excel("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/excels (raw data)/20220719_Synthego_DDR_KO_library_rep_1.xlsx")
rep_2_wells_p1, rep_2_wells_p2, rep_2_mn_p1, rep_2_mn_p2 = read_excel("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/excels (raw data)/20221107_Synthego_DDR_screen_rep_2.xlsx")
rep_3_wells_p1, rep_3_wells_p2, rep_3_mn_p1, rep_3_mn_p2 = read_excel("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/excels (raw data)/20221128_Synthego_DDR_screen_rep_3.xlsx")

calc_statistics(rep_2_mn_p1)

#Create excel file and sheet to contain all data
workbook = xlsxwriter.Workbook("Extracted Params.xlsx")
worksheet1 = workbook.add_worksheet("Rep 1 Outputs")
worksheet2 = workbook.add_worksheet("Rep 2 Outputs")
worksheet3 = workbook.add_worksheet("Rep 3 Outputs")

def write_sheet(sheet, p1_wells, p2_wells, p1_mn, p2_mn):
    sheet.write(0, 0, "Plate 1 Well ID")
    sheet.write(0, 1, "Plate 1 x maxes")
    sheet.write(0, 2, "Plate 1 max MN ratio")
    sheet.write(0, 3, "Plate 1 MSQ Error")
    sheet.write(0, 5, "Plate 2 Well ID")
    sheet.write(0, 6, "Plate 2 xmaxes")
    sheet.write(0, 7, "Plate 2 max MN ratio")
    sheet.write(0, 8, "Plate 2 MSQ Error")

    output1 = calc_statistics(p1_mn)
    output2 = calc_statistics(p2_mn)

    for row, name in enumerate(p1_wells):
        sheet.write(row + 1, 0, name)
    for row, name in enumerate(output1[0]):
        sheet.write(row + 1, 1, name)
    for row, name in enumerate(output1[1]):
        sheet.write(row + 1, 2, name)
    for row, name in enumerate(output1[2]):
        sheet.write(row + 1, 3, name)
    
    for row, name in enumerate(p2_wells):
        sheet.write(row + 1, 5, name)
    for row, name in enumerate(output2[0]):
        sheet.write(row + 1, 6, name)
    for row, name in enumerate(output2[1]):
        sheet.write(row + 1, 7, name)
    for row, name in enumerate(output2[2]):
        sheet.write(row + 1, 8, name)
    
    sheet.autofit()

#write_sheet(worksheet1, rep_1_wells_p1, rep_1_wells_p2, rep_1_mn_p1, rep_1_mn_p2)
#write_sheet(worksheet2, rep_2_wells_p1, rep_2_wells_p2, rep_2_mn_p1, rep_2_mn_p2)
#write_sheet(worksheet3, rep_3_wells_p1, rep_3_wells_p2, rep_3_mn_p1, rep_3_mn_p2)
#workbook.close()

# ===================================================================================================
# New wells and parameter lists need to be made because Kate was missing some wells
    
# List the indices from highest to lowest, that way removing wells will not affect the
# order of wells before it
pop_rep_1 = [99, 77, 55, 33, 11]
pop_rep_3 = [291, 269, 247, 225]

for m in pop_rep_1:
    rep_1_mn_p1.pop(m)
    rep_1_wells_p1.pop(m)

    rep_2_mn_p1.pop(m)
    rep_2_wells_p1.pop(m)

for n in pop_rep_3:
    rep_3_mn_p1.pop(n)
    rep_3_wells_p1.pop(n)

# Standard deviation of the mean "c" values should be graphed to find threshold
#c_rep1_p1 = calc_statistics(rep_1_mn_p1)[1]
#c_rep1_p2 = calc_statistics(rep_1_mn_p2)[1]
#c_rep2_p1 = calc_statistics(rep_2_mn_p1)[1]
#c_rep2_p2 = calc_statistics(rep_2_mn_p2)[1]
#c_rep3_p1 = calc_statistics(rep_3_mn_p1)[1]
#c_rep3_p2 = calc_statistics(rep_3_mn_p2)[1]

#standard_deviations = []

# Find standard deviations for all wells in plate 1
#i = 0
#while i < len(c_rep1_p1):
#    temp_list = []
#    temp_list.append(c_rep1_p1[i])
#    temp_list.append(c_rep2_p1[i])
#    temp_list.append(c_rep3_p1[i])
#    standard_deviations.append(statistics.stdev(temp_list))
#    i += 1

# Find standard deivations for all wells in plate 2
#i = 0
#while i < len(c_rep1_p2):
#    temp_list = []
#    temp_list.append(c_rep1_p2[i])
#    temp_list.append(c_rep2_p2[i])
#    temp_list.append(c_rep3_p2[i])
#    standard_deviations.append(statistics.stdev(temp_list))
#    i += 1

#plt.hist(standard_deviations, bins = 25)
#plt.ylabel("Number of wells")
#plt.xlabel("Standard deviation of c coefficient")
#plt.show()

# CALCULATING AND PLOTTING CORRELATION COEFFICIENTS
#rep_1_correl_p1 = calc_statistics(rep_1_mn_p1)[3]
#rep_1_correl_p2 = calc_statistics(rep_1_mn_p2)[3]
#rep_2_correl_p1 = calc_statistics(rep_2_mn_p1)[3]
#rep_2_correl_p2 = calc_statistics(rep_2_mn_p2)[3]
#rep_3_correl_p1 = calc_statistics(rep_3_mn_p1)[3]
#rep_3_correl_p2 = calc_statistics(rep_3_mn_p2)[3]

#plt.hist(rep_1_correl_p1 + rep_1_correl_p2 + rep_2_correl_p1 + rep_2_correl_p2 + rep_3_correl_p1 + rep_3_correl_p2, bins = 1000)
#plt.xlim(0, 0.0006)
#plt.ylabel("Number of wells")
#plt.xlabel("Mean Square Error")
#plt.show()

# ===================================================================================================
# Make a new excel file with updated wells and statistics
# Probably gonna start doing the rest of the analysis on a separate .py file since this one is clogged
#Create excel file and sheet to contain all data
workbook = xlsxwriter.Workbook("Newest Params 2.xlsx")
worksheet1 = workbook.add_worksheet("Rep 1 Outputs")
worksheet2 = workbook.add_worksheet("Rep 2 Outputs")
worksheet3 = workbook.add_worksheet("Rep 3 Outputs")

write_sheet(worksheet1, rep_1_wells_p1, rep_1_wells_p2, rep_1_mn_p1, rep_1_mn_p2)
write_sheet(worksheet2, rep_2_wells_p1, rep_2_wells_p2, rep_2_mn_p1, rep_2_mn_p2)
write_sheet(worksheet3, rep_3_wells_p1, rep_3_wells_p2, rep_3_mn_p1, rep_3_mn_p2)
workbook.close()