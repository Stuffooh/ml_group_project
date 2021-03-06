import os
import sys
import re
import numpy as np
from scipy.io import savemat
from progress import ProgressBar

CATEGORIES = ["02691156", "02773838", "02954340", "02958343", "03001627",
              "03261776", "03467517", "03624134", "03636649", "03642806",
              "03790512", "03797390", "03948459", "04099429", "04225987", "04379243"]

CATEGORY_NAMES = ['airplane', 'bag', 'cap', 'car', 'chair',
                 'earphone', 'guitar', 'knife', 'lamp', 'laptop',
                 'motorbike', 'mug', 'pistol', 'rocket', 'skateboard', 'table']

USAGE = """\
Usage:  convert-to-mat point-files-directory labels-file mat-dir

    point-files-directory : where to look for category-directories?
    labels-file : csv file with model IDs, categories and subcategories
    mat-dir : where to save the mat-files?
"""

if len(sys.argv) < 4:
    print(USAGE)
    exit(0)

POINTS_DIRECTORY = sys.argv[1]
LABELS_FILE_NAME = sys.argv[2]
MATDIR = sys.argv[3]

print(f"Points: {POINTS_DIRECTORY}\nLabels: {LABELS_FILE_NAME}\nMat dir: {MATDIR}")
if input("Coninue? (yes/no) ").strip() != "yes": exit(0)

print("Avaliable categories:")
print(' '.join(CATEGORY_NAMES))
chosen_categories = input("Which categories to use? (write names separated by space) ").strip().lower().split(" ")
CATEGORIES = [CATEGORIES[CATEGORY_NAMES.index(c)] for c in chosen_categories]


def read_csv(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(map(str.strip, re.split(r'[,;]', row)))[:3]


def index(values):
    return {value: i for i, value in enumerate(sorted(set(values)))}


def extract_points_from_obj(data):
    for match in re.findall(r'v\s*([\d.-]+)\s*([\d.-]+)\s*([\d.-]+)', data):
        yield tuple(map(float, match))


def read_obj_file(category, mod_id):
    file_name = f"model_{mod_id}.obj"
    file_path = os.path.join(POINTS_DIRECTORY, file_name)
    try:
        with open(file_path) as obj:
            return tuple(extract_points_from_obj(obj.read()))
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

print(f"NUMBER OF SUB-CATEGORIES: {len(LABEL_INDEX)}")
print(f"NUMBER OF CATEGORIES: {len(CATEGORY_INDEX)}")
print("ORDER OF CATEGORIES: ", end="")
print(' '.join((chosen_categories[CATEGORIES.index(k)]
                for k, v in sorted(CATEGORY_INDEX.items(),
                                   key=lambda itm: itm[1]))))



if input("Continue? (yes/no) ").strip() != "yes": exit(0)

def convert_obj_to_mat(model_id, category, label):
    coords = read_obj_file(category, model_id)
    if coords is None: return
    point_array = np.array(coords)
    label_array = np.ones((1, len(coords))) + LABEL_INDEX[label]
    category_array = np.ones((1, 1)) * CATEGORY_INDEX[category]
    savemat(os.path.join(MATDIR, f'{model_id}.mat'),
            {'points': point_array, 'labels': label_array, 'category': category_array})

print(f"Creating {len(labels)} files")
progress_step = max(len(labels) // 1000, 1)
progress_bar = ProgressBar(len(labels))
for i, (model_id, category, label) in enumerate(labels):
    if i % progress_step == 0:
        progress_bar.update(i)
    convert_obj_to_mat(model_id, category, label)
print('')


