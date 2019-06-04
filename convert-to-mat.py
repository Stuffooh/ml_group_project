import os
import sys
import re
from collections import defaultdict
import numpy as np
from scipy.io import savemat

CATEGORIES = ["02691156", "02773838", "02954340", "02958343", "03001627", 
             "03261776", "03467517", "03624134", "03636649", "03642806",
             "03790512", "03797390", "03948459", "04099429", "04225987", "04379243"]

usage = """\
Usage:  convert-to-mat point-files-directory labels-file mat-dir

    point-files-directory : where to look for category-directories?
    labels-file : csv file with model IDs, categories and subcategories
    mat-dir : where to save the mat-files?

Good luck!
"""

if len(sys.argv) < 4:
    print(usage)
    exit(0)

POINTS_DIRECTORY = sys.argv[1]
LABELS_FILE_NAME = sys.argv[2]
MATDIR = sys.argv[3]

print(f"Points: {POINTS_DIRECTORY}\nLabels: {LABELS_FILE_NAME}\nMat dir: {MATDIR}")

yes = input("Good? Type yes... ")
if yes.strip() != "yes":
    exit(0)



def read_csv(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(num.strip() for num in re.split(r'[,;]', row))


def index(values):
    return {value: i for i, value in enumerate(set(values))}


def extract_points_from_obj(data):
    for match in re.findall(r'v\s*([\d.-]+)\s*([\d.-]+)\s*([\d.-]+)', data):
        yield tuple(map(float, match))


def read_obj_file(category, mod_id):
    file_name = f"model_{mod_id}.obj"
    file_path = os.path.join(POINTS_DIRECTORY, category, file_name)
    try:
        with open(file_path) as f:
            return tuple(extract_points_from_obj(f.read()))
    except FileNotFoundError:
        print(f"{file_path} not found, skipping..")
        return None
    except ValueError:
        print(f"Error reading file {file_path}, skipping...") 
        return None



with open(LABELS_FILE_NAME, 'r') as f:
    labels = read_csv(f.read())

labels = [row for row in labels
          if row[1] in CATEGORIES]

LABEL_INDEX = index([row[2] for row in labels])
CATEGORY_INDEX = index(CATEGORIES)


def obj2mat(mid, category, label):
    coords = read_obj_file(category, mid)
    if coords is None: return
    point_array = np.array(coords)
    label_array = np.ones((1, len(coords))) + LABEL_INDEX[label]
    category_array = np.ones((1, 1)) * CATEGORY_INDEX[category]
    savemat(os.path.join(MATDIR, f'{mid}.mat'),
            {'points': point_array, 'labels': label_array, 'category': category_array})


for model_id, category, label in labels:
    print(f"Created file {model_id}.mat")
    obj2mat(model_id, category, label)

"""
def create_category_mat(category, model_ids, labels):
    label_array = []
    point_array = []

    for mid, label in zip(model_ids, labels):
        coords = read_obj_file(category, mid)
        if coords is None:
            continue
        label_array.extend([LABEL_INDEX[label]] * len(coords))
        point_array.extend(coords)

    n = len(point_array)
    # labels +1 
    label_array = np.array(label_array).reshape(n, 1) + 1
    point_array = np.array(point_array).reshape(n, 3)
    category_array = np.array([[CATEGORY_INDEX[category]]])
 
    savemat(os.path.join(MATDIR, f'{category}.mat'),
            {'points': point_array, 'labels': label_array, 'category': category_array})



print('Extracting points...')
categories_grouped = defaultdict(lambda: {'labels': list(), 'models': list()})

for mid, category, label in zip(model_ids, categories, labels):
    categories_grouped[category]['models'].append(mid)
    categories_grouped[category]['labels'].append(label)


for cid, category in categories_grouped.items():
    print(f"Category: {cid}")
    create_category_mat(cid, category['models'], category['labels'])

print("done")

"""
