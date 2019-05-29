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

points_directory = sys.argv[1]
labels_fname = sys.argv[2]
matdir = sys.argv[3]

print(f"Points: {points_directory}\nLabels: {labels_fname}\nMat dir: {matdir}")

yes = input("Good? Type yes... ")
if yes.strip() != "yes":
    exit(0)


print('Extracting labels -- ', end="")

def extract_labels(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(num.strip()
                    for num in re.split(r'[,;]', row))

categories = defaultdict(lambda: {'labels': list(), 'models': list()})

with open(labels_fname, 'r') as f:
    labels_raw = f.read()

for mid, category, label in extract_labels(labels_raw):
    categories[category]['models'].append(mid)
    categories[category]['labels'].append(label)

print("done")

def index(values):
    return {value: i for i, value in enumerate(set(values))}

from itertools import chain
label_index = index(chain(*(category['labels']
                            for category in categories.values())))
category_index = index(categories.keys())


def create_category_mat(category, model_ids, labels):

    def extract_points(data):
        for match in re.findall(r'v\s*([\d.-]+)\s*([\d.-]+)\s*([\d.-]+)', data):
            yield tuple(map(float, match))


    label_array = []
    point_array = []

    for mid, label in zip(model_ids, labels):
        try:
            with open(os.path.join(points_directory, category, f"model_{mid}.obj")) as f:
                coords  = tuple(extract_points(f.read()))
        except FileNotFoundError:
            print(f"File model_{mid}.obj not found, skipping..")
            continue
        except ValueError:
            print(f"Error reading file model_{mid}.obj, skipping...") 
            continue

        label_array.extend([label_index[label]] * len(coords))
        point_array.extend(coords)

    n = len(point_array)
    # labels +1 
    label_array = np.array(label_array).reshape(n, 1) + 1
    point_array = np.array(point_array).reshape(n, 3)
    category_array = np.array([[category_index[category]]])
 
    savemat(os.path.join(matdir, f'{category}.mat'),
            {'points': point_array, 'labels': label_array, 'category': category_array})



print('Extracting points...')

for cid, category in categories.items():
    print(f"Category: {cid}")
    create_category_mat(cid, category['models'], category['labels'])

print("done")

