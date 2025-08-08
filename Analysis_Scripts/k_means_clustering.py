# ===================================================================================================
# Date: July 24, 2025
# Author: Andrew Tian
# This code was made to average each of the wells
# and perform the k-means clustering on Kate's data
from excel_reader import read_sheet2, extract_well_map, extract_DDR_map
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import xlsxwriter
from statsmodels.stats.weightstats import ztest
import statsmodels.stats.multitest as smm
import heapq
from scipy import stats
from functions import zscore, right_p_vals
from statistics import stdev

# Each "rep" variable is a list containing 5 things:
#     rep[0] contains the list of well IDs
#     rep[1] contains the list of "b" parameters
#     rep[2] contains the list of "c" parameters
#     rep[3] contains the list of max mn ratio points
#     rep[4] contains the list of mean square errors
rep1_p1, rep1_p2 = read_sheet2("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/Newest Params 2.xlsx", 0)
rep2_p1, rep2_p2 = read_sheet2("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/Newest Params 2.xlsx", 1)
rep3_p1, rep3_p2 = read_sheet2("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/Newest Params 2.xlsx", 2)

# Start taking averages of all parameters
def avg(rep1, rep2, rep3):
    output = []
    i = 0
    while i < len(rep1):
        output.append((rep1[i] + rep2[i] + rep3[i])/3)
        i += 1
    return output

p1_x = avg(rep1_p1[1], rep2_p1[1], rep3_p1[1])
p1_mn = avg(rep1_p1[2], rep2_p1[2], rep3_p1[2])
p1_stdev = []
i = 0
while i < len(rep1_p1[2]):
    p1_stdev.append(stdev([rep1_p1[2][i], rep2_p1[2][i], rep3_p1[2][i]]))
    i += 1

p2_x = avg(rep1_p2[1], rep2_p2[1], rep3_p2[1])
p2_mn = avg(rep1_p2[2], rep2_p2[2], rep3_p2[2])
p2_stdev = []
i = 0
while i < len(rep1_p2[2]):
    p2_stdev.append(stdev([rep1_p2[2][i], rep2_p2[2][i], rep3_p2[2][i]]))
    i += 1

# Scale the mn ratios since they are smaller
p1_scale = []
for num in p1_mn:
    p1_scale.append(num * 2500)

p2_scale = []
for num in p2_mn:
    p2_scale.append(num * 2500)

data = np.array([p1_x + p2_x, p1_scale + p2_scale])
#data = np.array([p1_x + p2_x, p1_mn + p2_mn])
data = data.transpose()

# Perform K-Means Clustering
# Elbow plot to see optimal number of clusters
i = 0
wcss = []
for i in range(1, 15):
    model = KMeans(n_clusters = i, n_init = 1, init = 'k-means++')
    model.fit(data)
    wcss.append(model.inertia_)
fig = plt.figure(figsize = (7, 7))
plt.plot(range(1, 15), wcss, linewidth = 4, markersize = 12, marker = 'o', color = 'orange')
plt.xticks(np.arange(15))
plt.xlabel("Number of clusters")
plt.ylabel("WCSS")
plt.show()

# Seems like 6 is probably the optimal number of clusters based on the elbow plot
model = KMeans(n_clusters = 6, init = "k-means++", max_iter = 300, n_init = 10, random_state = 0)
y_clusters = model.fit_predict(data)
labels = model.labels_

fig = plt.figure(figsize = (15, 15))
ax = fig.add_subplot()

colours = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'aqua', 'gold', 'pink']

def scatter_points(graph, data_points, cluster_points, size, colour_list, n):
    for i in range(n):
        graph.scatter(data_points[cluster_points == i, 0], data_points[cluster_points == i, 1], s = size, c = colour_list[i])

scatter_points(ax, data, y_clusters, 15, colours, 6)
ax.scatter(model.cluster_centers_[:,0], model.cluster_centers_[:,1], s = 75, c = "black")
ax.set_xlabel("Time of peak MN Ratio (hours)")
ax.set_ylabel("Peak MN Ratio (x2500)")
ax.legend()
plt.show()

# Silhouette values to determine the fit of each cluster
silhouette_avg = silhouette_score(data, y_clusters)
sample_silhouette_values = silhouette_samples(data, y_clusters)

# Extract the genes from each well and assign them to an index in the overall list combining both plates
DDR_map = extract_DDR_map("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/New_DDR_Map.xlsx", 0)
well_map1 = extract_well_map("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/Plate_Maps.xlsx", 0)
well_map2 = extract_well_map("/Users/andrewtian/Documents/HardingLab/Exp_Kate_Analysis/Plate_Maps.xlsx", 1)

# Create gene list in the corresponding order as the well list and the labels in order to group them
gene_list = []
i = 0
while i < len(rep1_p1[0]):
    gene_list.append(well_map1[rep1_p1[0][i]])
    i += 1
i = 0
while i < len(rep1_p2[0]):
    gene_list.append(well_map2[rep1_p2[0][i]])
    i += 1

# Create a dictionary with each cluster and its corresponding genes
cluster_genes = {}
cluster_mn = {}
all_mn = p1_mn + p2_mn
all_stdev = p1_stdev + p2_stdev

i = 0
while i < len(labels):
    if labels[i] not in cluster_genes:
        cluster_genes[labels[i]] = [gene_list[i]]
        cluster_mn[labels[i]] = [all_mn[i]]
    else:
        cluster_genes[labels[i]].append(gene_list[i])
        cluster_mn[labels[i]].append(all_mn[i])
    i += 1

# Extract cluster centroids (list of all cluster center values)
cluster_centroids = model.cluster_centers_

# Calculate standard deviations for each cluster
cluster_stdev = []

for key in cluster_mn:
    cluster_stdev.append(stdev(cluster_mn[key]))

# Write the cluster data onto a new excel
#workbook = xlsxwriter.Workbook("DDR Pathway Clustering 2.xlsx")
#worksheet1 = workbook.add_worksheet("Data")

#worksheet1.write(0, 0, "Cluster")
#worksheet1.write(0, 1, "Colour")
#worksheet1.write(0, 2, "Time of Peak MN Ratio of Cluster (hours)")
#worksheet1.write(0, 3, "Mean Peak MN Ratio of Cluster")
#worksheet1.write(0, 4, "BER/SSBR")
#worksheet1.write(0, 5, "FA/ICL")
#worksheet1.write(0, 6, "FORK QC")
#worksheet1.write(0, 7, "HR")
#worksheet1.write(0, 8, "MMR")
#worksheet1.write(0, 9, "NER")
#worksheet1.write(0, 10, "EJ")
#worksheet1.write(0, 11, "RER")
#worksheet1.write(0, 12, "OTHER")

#i = 0
#for i in range(len(cluster_list)):
#    worksheet1.write(i + 1, 0, i)
#    worksheet1.write(i + 1, 1, colours[i])
#    worksheet1.write(i + 1, 2, cluster_centroids[i][0])
#    worksheet1.write(i + 1, 3, cluster_centroids[i][1] / 2500)
#    temp_list = cluster_list[i]
#    w = 0
#    for pathway, genes in DDR_map.items():
#        n = 0
#        for item in genes:
#            if item in temp_list:
#                n += 1
#        worksheet1.write(i + 1, 4 + w, n)
#        w += 1
#worksheet1.autofit()
#workbook.close()

# ===================================================================================================
# Determine statistical significance in the MN ratio between
# each of the clusters and the control cluster using a z-test
# also need to run a FDR to account for false positives
z_test = {}
alpha_mn = {}
for key in cluster_mn:
    p = 0
    data_arr = []
    if key != 4:
        z_score, p_val = ztest(np.array(cluster_mn[key]), np.array(cluster_mn[4]), value = 0)
        # Make sure to multiply the p value by 2 for a two-tailed z-test
        z_test[key] = [z_score, p_val * 2]
        #print(str(key) + ": " + str(z_test[key]))

# Run a boneferroni correction
new_a = 0.05/len(z_test)
#for ind in z_test:
#    if z_test[ind][1] < new_a:
#        print(str(ind) + ": Reject Null")
#    else:
#        print(str(ind) + ": Accept Null")

# Get all largest genes in largest cluster
indexed_mn = [(value, index) for index, value in enumerate(all_mn)]
sorted_mn = heapq.nlargest(25, indexed_mn, key = lambda x: x[0])
largest_mn = []
largest_mn_stdev = []
largest_mn_indexes = []
largest_genes = []
for pair in sorted_mn:
    largest_mn.append(pair[0])
    largest_mn_indexes.append(pair[1])
for ind in largest_mn_indexes:
    largest_genes.append(gene_list[ind])
    largest_mn_stdev.append(all_stdev[ind])

# Compare largest genes to control to generate list of z-scores, first plot all genes to see distribution
plt.hist(all_mn, bins = 25, edgecolor = 'black')
plt.xlabel("Peak MN Ratio")
plt.ylabel("Frequency")
plt.title("Distribution of peak MN ratios across DDR screen")
plt.show()

# Calculate all z-scores, first do the control and test the largest genes
# Run a false discovery rate to reduce the risk of false positives; use Benjamini Hochberg since there's many tests
# The control nt RNA #1 should be at index 327
# Calculating z-score for control, use a LEFT HANDED one-sided p value to test
ntrna_z = zscore([all_mn[327]], all_mn)
ntrna_p = stats.norm.cdf(ntrna_z[0])
print(all_mn[327])
print(all_stdev[327])
#print(ntrna_z)
#print(ntrna_p)
# z = -1.87, p = 0.03, so since p < 0.05 it is significant

# Calculating all remaining significant z-scores
z_scores = zscore(largest_mn, all_mn)
p_vals = right_p_vals(z_scores)

# Perform benjamini hochberg correction, p list is already ranked in ascending order
# use a higher false discovery rate of about 5% maybe?
bh_vals = []
# Perform Benjamini-Hochberg correction
reject, pvals_corrected, alphacSidak, alphacBonf = smm.multipletests(p_vals, alpha=0.05, method='fdr_bh')
hit_pathways = []
for gene in largest_genes:
    path_list = []
    for key, value in DDR_map.items():
        if gene in value:
            path_list.append(key)
    if len(path_list) == 0:
        path_list.append("None")
    hit_pathways.append(path_list)

#print("Original p-values:", p_vals)
#print("Adjusted p-values (Benjamini-Hochberg):", pvals_corrected)
#print("Rejected hypotheses:", reject)

#workbook = xlsxwriter.Workbook("Gene testing.xlsx")
#worksheet1 = workbook.add_worksheet("Data")

#worksheet1.write(0, 0, "gene")
#worksheet1.write(0, 1, "mn_ratio")
#worksheet1.write(0, 2, "std_dev")
#worksheet1.write(0, 3, "z-score")
#worksheet1.write(0, 4, "p-value")
#worksheet1.write(0, 5, "adjusted p-value")
#worksheet1.write(0, 6, "reject Null?")
#worksheet1.write(0, 7, "labelled pathway")

#for i in range(25):
#    worksheet1.write(i + 1, 0, largest_genes[i])
#    worksheet1.write(i + 1, 1, largest_mn[i])
#    worksheet1.write(i + 1, 2, largest_mn_stdev[i])
#    worksheet1.write(i + 1, 3, z_scores[i])
#    worksheet1.write(i + 1, 4, p_vals[i])
#    worksheet1.write(i + 1, 5, pvals_corrected[i])
#    worksheet1.write(i + 1, 6, reject[i])
#    worksheet1.write(i + 1, 7, hit_pathways[i][0])
#worksheet1.autofit()
#workbook.close()