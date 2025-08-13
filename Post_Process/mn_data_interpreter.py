# ==================================================================================================
# Author: Andrew Tian
# Date Written: May 14th, 2025
# This library was developed in order to interpret the .json
# outputs of the MicroNuclei_Detection software, the GitHub
# to that software can be found here:
# https://github.com/kew6688/MicroNuclei_Detection

import json
from natsort import natsorted
from collections import Counter
import numpy as np

# parse_text will split a chunk of text based on two string inputs as well as two integer
# values that take a distance from each of the string inputs
def parse_text(text, str1, str2, d1 = 0, d2 = 0):
    newtext = ""
    a = text.find(str1)
    b = text.find(str2)
    newtext = text[a + d1:b - d2]
    return newtext

# get_float_list will return a list of float values (used especially for scoring predictions)
def get_float_list(text):
    # float_list is the final list of floats to be outputted
    float_list = []

    # c is used to index the commas separating each float
    # n is the actual variable used to store and append floats to the list
    c = 0
    n = 0

    # check if the list is empty
    if text != "[]":
        # while loop repeatedly parses through the list of floats
        while text.find(",") != -1:
            c = text.find(",")
            n = float(text[1:c])
            float_list.append(n)
            text = text[c + 1:]
        # try except used to check if the list is only one float long
        # it would bypass the while loop as a singular item has no commas
        try:
            float_list.append(float(text[:-1]))
        except:
            float_list.append(float(text[1:-1]))
    return float_list

# get_coords_list will return a list of coordinates (integer)
# n is used in case the numbers are floats; can index how many characters away a period is
def get_coords_list(text, n = 0):
    # a and b look for an overall list with double brackets
    a = text.find("[[")
    b = text.find("]]")
    
    # c, d, and e are used to index the brackets and the comma
    c = 0
    d = 0
    e = 0

    # f is used to store and append all integer values
    f = 0

    # coord_text stores the text containing all the coordinates in an image
    # box_text is the string representing an individual set of coordinates
    # coord_box stores an individual set of coordinates
    # coords_list represents the list of all coordinates in an image
    coord_text = ""
    box_text = ""
    coord_box = []
    coords_list = []

    coord_text = text[a + 1:b + 1]

    # Check to make sure that the list isn't empty
    if coord_text != "":
        # while loop repeatedly parses each set of coordinates by the brackets
        while coord_text.find("]") != -1:
            coord_box = []
            c = coord_text.find("[")
            d = coord_text.find("]")
            box_text = coord_text[c:d + 1]

            # while loop repeatedly parses the commas to extract values
            while box_text.find(",") != -1:
                e = box_text.find(",")
                f = int(box_text[1:e - n])
                coord_box.append(f)
                box_text = box_text[e + 1:]

            # extracts the remaining value
            f = int(box_text[1:-(1 + n)])
            coord_box.append(f)
            coords_list.append(coord_box)

            # try/except ensures that the loop doesn't crash at the final value
            try:
                coord_text = coord_text[d + 1:]
            except:
                break
        return coords_list
    else:
        return []

# read_text breaks down the large .json file into
# each image's individual data and stores it in a list
def read_text(path_to_json):
    # Initializing variables
    # n and i are used to count the number of 
    # a and b are used to parse the raw text file
    n = 0
    i = 0
    a = 0
    b = 0

    # raw_text is the total json text stored as a string
    # temp is used as a placeholder to parse raw_text
    raw_text = ""
    temp = ""

    # image_texts is a list containing the broken down 
    # info from each image's block of information
    image_texts = []
    
    # Open the json file
    raw_text = json.dumps(json.load(open(path_to_json, "r")))
    n = raw_text.count("image")

    # while loop continually breaks down the large
    # raw text into individual image texts
    while i < n:
        a = raw_text.find('{"image"')
        b = raw_text.find("}}")
        temp = raw_text[a:b + 2]
        image_texts.append(temp)
        raw_text = raw_text[b + 3:]
        i += 1

    # return the list
    return(image_texts)

# get_image_ids breaks down a given json file
# into a list containing all image ids
def get_image_ids(path_to_json):
    # b is used to index the end of the image ID
    b = 0

    # image_texts is the list of all image info
    # image_ids is the list of all image IDs
    image_texts = read_text(path_to_json)
    image_ids = []
    
    # for loop continually returns all image IDs
    for image in image_texts:
        b = image.find(', "n')
        image_ids.append(image[11:b - 1])

    # return the list
    return image_ids

# get_nuclei_info breaks down a given json file
# into a list containing only the nuclei info
def get_nuclei_info(path_to_json):
    # a is used to index the start of nuclei info
    # b is used to index the end of nuclei info
    a = 0
    b = 0

    # image_texts is the list of all image infos
    # nuclei_texts is the list of all image nuclei info
    image_texts = read_text(path_to_json)
    nuclei_texts = []

    # for loop continually extracts all nuclei info
    # and adds it to a list to be outputted
    for image in image_texts:
        a = image.find('"nuclei"')
        b = image.find('"micronuclei"')
        nuclei_texts.append(image[a:b - 2])

    # return the list
    return nuclei_texts

# get_micronuclei_info breaks down a given json file
# into a list containing only the micronuclei info
def get_micronuclei_info(path_to_json):
    # a is used to index the start of micronuclei info
    # b is used to index the end of micronuclei info
    a = 0
    b = 0

    # image_texts is the list of all image infos
    # micronuclei_texts is the list of all image micronuclei info
    image_texts = read_text(path_to_json)
    micronuclei_texts = []

    # for loop continually extracts all nuclei info
    # and adds it to a list to be outputted
    for image in image_texts:
        a = image.find('"micronuclei"')
        b = image.find('}}')
        micronuclei_texts.append(image[a:b + 1])

    # return the list
    return micronuclei_texts

# get_nuclei_coords() returns a list of lists, each individual
# list contains all the center coordinates for all the nuclei in an image
# and the overall outputted list contains all image's lists
def get_nuclei_coords(path_to_json):
    nuclei_texts = get_nuclei_info(path_to_json)
    nuclei_coord_texts = []
    json_coords = []

    for text in nuclei_texts:
        nuclei_coord_texts.append(parse_text(text, '"coord"', ', "area"', 0, 0))
    
    for item in nuclei_coord_texts:
        json_coords.append(get_coords_list(item, 2))
    
    return(json_coords)

# get_micronuclei_coords() returns a list of lists, each individual
# list contains all the center coordinates for all the micronuclei in an image
# and the overall outputted list contains all image's lists
def get_micronuclei_coords(path_to_json):
    micronuclei_texts = get_micronuclei_info(path_to_json)
    micronuclei_coord_texts = []
    json_coords = []

    for text in micronuclei_texts:
        micronuclei_coord_texts.append(parse_text(text, '"coord"', ', "area"', 0, 0))
    
    for item in micronuclei_coord_texts:
        json_coords.append(get_coords_list(item, 0))
    
    return(json_coords)

# get_nuclei_counts returns a list of each image's number of nuclei
# based on the number of center coordinates given
def get_nuclei_counts(path_to_json):
    # nuclei_coords are the nuclei coordinates for each image
    # nuclei_counts are the nuclei counts for each image
    nuclei_coords = get_nuclei_coords(path_to_json)
    nuclei_counts = []

    for coords in nuclei_coords:
        nuclei_counts.append(len(coords))

    # return the number of nuclei
    return nuclei_counts

# get_micronuclei_counts returns a list of each image's number of nuclei
# based on the number of center coordinates given
def get_micronuclei_counts(path_to_json):
    # micronuclei_coords are the micronuclei coordinates for each image
    # micronuclei_counts are the micronuclei counts for each image
    micronuclei_coords = get_micronuclei_coords(path_to_json)
    micronuclei_counts = []

    for coords in micronuclei_coords:
        micronuclei_counts.append(len(coords))

    # return the number of micronuclei
    return micronuclei_counts

# get_mn_ratios returns a list of micronuclei ratios given
# a json file, using the nuclei & micronuclei counts
def get_mn_ratios(path_to_json):
    # nuclei_counts is the list of the number of nuclei in each image
    # micronuclei_counts is the list of the number of micronuclei in each image
    # mn_ratios is the list of micronuclei ratios
    # r is a variable to temporarily store the micronuclei ratio
    nuclei_counts = get_nuclei_counts(path_to_json)
    micronuclei_counts = get_micronuclei_counts(path_to_json)
    mn_ratios = []
    r = 0

    # for loop continually calculates the ratio values
    for n, m in zip(nuclei_counts, micronuclei_counts):
        if n != 0:
            r = m / n
            mn_ratios.append(r)
        else:
            mn_ratios.append("null")

    # return updated list
    return mn_ratios

# get_parent_maps gets a list of parent nuclei indexes which corresponds to
# the order of micronuclei that they align with
def get_parent_maps(path_to_json):
    micronuclei_texts = get_micronuclei_info(path_to_json)
    parent_texts = []
    parent_list = []
    temp_list = []
    int_list = []

    for text in micronuclei_texts:
        parent_texts.append(parse_text(text, '"parent":', '}', 10, 0))

    for item in parent_texts:
        temp_list = get_float_list(item)
        int_list = []
        for num in temp_list:
            int_list.append(int(num))
        parent_list.append(int_list)

    return(parent_list)

# get_parent_distances takes the distance between micronuclei centers and
# their nuclei centers as well
def get_parent_distances(path_to_json):
    parent_map = get_parent_maps(path_to_json)
    nuclei_centers = get_nuclei_coords(path_to_json)
    mn_centers = get_micronuclei_coords(path_to_json)

    temp_dist = []
    file_dist = []

    n = 0
    m = 0
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    d = 0

    for map in parent_map:
        temp_dist = []
        n = parent_map.index(map)
        for i in map:
            m = map.index(i)

            x1 = nuclei_centers[n][i][0]
            y1 = nuclei_centers[n][i][1]

            x2 = mn_centers[n][m][0]
            y2 = mn_centers[n][m][1]

            d = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            temp_dist.append(d)
        file_dist.append(temp_dist)
    return(file_dist)

# jsonFile class stores all the processed information about
# each image into a singular object
class jsonFile:
    # Initialize variables
    def __init__(self, path_to_json):
        self.raw_text = read_text(path_to_json)
        self.image_ids = get_image_ids(path_to_json)
        self.nuclei_counts = get_nuclei_counts(path_to_json)
        self.micronuclei_counts = get_micronuclei_counts(path_to_json)
        self.nuclei_coords = get_nuclei_coords(path_to_json)
        self.micronuclei_coords = get_micronuclei_coords(path_to_json)
        self.mn_ratios = get_mn_ratios(path_to_json)
        self.parent_maps = get_parent_maps(path_to_json)
        self.parent_distances = get_parent_distances(path_to_json)
    
    # sort_alpha sorts the image IDs alphabetically as well as every other list correspondingly
    def sort_alpha(self):
        # alpha_dict maps the original image ID index to the new alphabetically sorted one
        # alpha_image_ids contains the alphabetically sorted list of image IDs
        alpha_dict = {}
        alpha_image_ids = []
        temp_list = []

        # a and b are used to map the nonsorted to the sorted indexes
        # n and i are just used in a loop to count 
        a = 0
        b = 0
        n = 0
        i = 0

        # create the alpha_dict value
        alpha_image_ids = natsorted(self.image_ids)
        for file in self.image_ids:
            a = self.image_ids.index(file)
            b = alpha_image_ids.index(file)
            alpha_dict[a] = b
        
        # for loop looks at every attribute in the object
        n = len(alpha_dict)
        for attr in self.__dict__:
            i = 0
            temp_list = []
            # while loop looks at every value within the attribute
            while i < n:
                # for loop used to map the original value to it's sorted position
                for key, value in alpha_dict.items():
                    if value == i:
                        temp_list.append(self.__dict__[attr][key])     
                i += 1
            self.__dict__[attr] = temp_list

    # calc_mn_ratios recalculates mn ratios using the object's nuc amd mn counts
    def calc_mn_ratios(self):
        # nuclei_counts is the list of the number of nuclei in each image
        # micronuclei_counts is the list of the number of micronuclei in each image
        # mn_ratios is the list of micronuclei ratios
        # r is a variable to temporarily store the micronuclei ratio
        nuclei_counts = self.nuclei_counts
        micronuclei_counts = self.micronuclei_counts
        mn_ratios = []
        r = 0

        # for loop continually calculates the ratio values
        for n, m in zip(nuclei_counts, micronuclei_counts):
            if n != 0:
                r = m / n
                mn_ratios.append(r)
            else:
                mn_ratios.append("null")

        # return updated list
        self.mn_ratios = mn_ratios

    # update_list updates a sublist in an overall list attribute
    def update_list(self, list, i, remove_indexes):
        remove_list = []

        for n in remove_indexes:
            remove_list.append(list[i][n])

        for item in remove_list:
            list[i].remove(item)

    # update_micronuclei updates all micronuclei-related attributes at a single index sublist
    def update_micronuclei(self, i, remove_indexes):
        self.micronuclei_counts[i] -= len(remove_indexes)
        self.update_list(self.micronuclei_coords, i = i, remove_indexes = remove_indexes)
        self.update_list(self.parent_maps, i = i, remove_indexes = remove_indexes)
        self.update_list(self.parent_distances, i = i, remove_indexes = remove_indexes)
        self.calc_mn_ratios()

    # apop_threshold removes groups of micronuclei 
    def apop_threshold(self, apop_cnt = 2):
        # n is the threshold for apoptosis
        n = apop_cnt

        # t indexes the image, i indexes individual micronuclei to be removed
        t = 0
        i = 0

        remove = []
        counts = {}

        for image_map in self.parent_maps:
            remove = []            
            counts = Counter(image_map)
            for x in counts:
                if counts[x] > n:
                    for i in range(len(image_map)):
                        if image_map[i] == x:
                            remove.append(i)
            remove.sort()
            self.update_micronuclei(t, remove)
            t += 1

    # dist_threshold removes micronuclei based on distance to assigned parent
    def dist_threshold(self, thresh = 25.0):
        n = thresh
        t = 0
        l = 0
        count = 0
        remove = []

        for dist_list in self.parent_distances:
            remove = []
            count = 0
            l = len(dist_list)
            while count < l:
                if dist_list[count] >= n:
                    remove.append(count)
                count += 1
            self.update_micronuclei(t, remove)
            t += 1
