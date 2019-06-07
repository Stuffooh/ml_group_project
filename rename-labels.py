import sys
import os
import re
from scipy.io import loadmat, savemat
from progress import ProgressBar


if len(sys.argv) != 5:
    print("Usage\n\trename-labels MAT_TRAIN_FILES_DIRECTORY MAT_TEST_FILES_DIRECTORY TRAIN_LABELS_CSV TEST_LABELS_CSV")
    exit(0)


MAT_TRAIN_DIRECTORY = sys.argv[1]
MAT_TEST_DIRECTORY = sys.argv[2]
TRAIN_LABEL_CSV = sys.argv[3]
TEST_LABEL_CSV = sys.argv[4]

def read_csv(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(map(str.strip, re.split(r'[,;]', row)))[:3]

with open(TRAIN_LABEL_CSV) as f:
    TRAIN_LABELS = {id: (cat, label) for id, cat, label in read_csv(f.read())}

with open(TEST_LABEL_CSV) as f:
    TEST_LABELS = {id: (cat, label) for id, cat, label in read_csv(f.read())}



category_indexes = dict()
subcategory_indexes = dict()

progress = ProgressBar(len(os.listdir(MAT_TRAIN_DIRECTORY)) + len(os.listdir(MAT_TEST_DIRECTORY)))
i = 0

for f in os.listdir(MAT_TRAIN_DIRECTORY):
    mat = loadmat(os.path.join(MAT_TRAIN_DIRECTORY, f))
    category = mat["category"]
    subcategory = mat["labels"]

    assert all(subcategory[:, 0] == subcategory[0, 0])

    category_index = category[0, 0]
    subcategory_index = subcategory[0, 0]

    id = f[:-4]
    category = TRAIN_LABELS[id][0]
    subcategory = TRAIN_LABELS[id][1]

    if category in category_indexes:
        assert category_indexes[category] == category_index
    if subcategory in subcategory_indexes:
        assert subcategory_indexes[subcategory] == subcategory_index

    category_indexes[category] = category_index
    subcategory_indexes[subcategory] = subcategory_index

    i += 1
    progress.update(i)


for f in os.listdir(MAT_TEST_DIRECTORY):
    mat = loadmat(os.path.join(MAT_TEST_DIRECTORY, f))

    id = f[:-4]
    category = TEST_LABELS[id][0]
    subcategory = TEST_LABELS[id][1]

    mat["category"] = mat["category"] * 0 + category_indexes[category]
    mat["labels"] = mat["labels"] * 0 + subcategory_indexes[subcategory]

    savemat(os.path.join(MAT_TEST_DIRECTORY, f), mat)

    i += 1
    progress.update(i)


