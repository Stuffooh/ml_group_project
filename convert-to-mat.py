import os
import sys
import re
from collections import defaultdict
import numpy as np
from scipy.io import savemat

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
LABELS_FNAME = sys.argv[2]
MATDIR = sys.argv[3]

print(f"Points: {POINTS_DIRECTORY}\nLabels: {LABELS_FNAME}\nMat dir: {MATDIR}")

yes = input("Good? Type yes... ")
if yes.strip() != "yes":
    exit(0)


def read_csv(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(num.strip() for num in re.split(r'[,;]', row))


def index(values):
    return {value: i for i, value in enumerate(set(values))}


def extract_points(data):
    for match in re.findall(r'v\s*([\d.-]+)\s*([\d.-]+)\s*([\d.-]+)', data):
        yield tuple(map(float, match))


def read_obj_file(category, mod_id):
    fname = f"model_{mod_id}.obj"
    try:
        with open(os.path.join(POINTS_DIRECTORY, category, fname)) as f:
            coords  = tuple(extract_points(f.read()))
        return coords
    except FileNotFoundError:
        print(f"{fname} not found, skipping..")
        return None
    except ValueError:
        print(f"Error reading file {fname}, skipping...") 
        return None


print('Extracting labels -- ', end="")

with open(LABELS_FNAME, 'r') as f:
    model_ids, categories, labels = tuple(zip(*read_csv(f.read())))

LABEL_INDEX = index(labels)
CATEGORY_INDEX = index(categories)

print("done")

categories_grouped = defaultdict(lambda: {'labels': list(), 'models': list()})

for mid, category, label in zip(model_ids, categories, labels):
    categories_grouped[category]['models'].append(mid)
    categories_grouped[category]['labels'].append(label)


CATEGORY_INDEX = index(list(categories_grouped.keys())[:15])

def obj2mat(mid, category, label):
    import random
    fake_label = random.randint(1, 50)
    coords = read_obj_file(category, mid)
    if coords is None:
        return
    n = len(coords)
    label_array = np.ones((1, n)) * fake_label
    point_array = np.array(coords)
    category_array = np.array([[CATEGORY_INDEX[category]]])
    savemat(os.path.join(MATDIR, f'{mid}.mat'),
            {'points': point_array, 'labels': label_array, 'category': category_array})



for category, ml in tuple(categories_grouped.items())[:15]:
    model_ids, labels = ml['models'], ml['labels']
    for model_id, label in zip(model_ids, labels):
        print(f"Created file {model_id}.obj")
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
