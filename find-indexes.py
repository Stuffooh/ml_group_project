import sys
import os
import json
import re
from scipy.io import loadmat


if len(sys.argv) != 3:
    print("Usage\n\tfind-indexes MAT_FILES_DIRECTORY LABELS_CSV_FILE\n\nOutputs\n\tjson data")
    exit(0)


MAT_DIRECTORY = sys.argv[1]
LABEL_CSV = sys.argv[2]

def read_csv(data):
    # skip first row, thats the headers
    for row in data.strip().split('\n')[1:]:
        yield tuple(map(str.strip, re.split(r'[,;]', row)))


with open(LABEL_CSV) as f:
    LABELS = {id: (cat, label) for id, cat, label in read_csv(f.read())}


category_indexes = dict()
subcategory_indexes = dict()

for f in os.listdir(MAT_DIRECTORY):
    mat = loadmat(os.path.join(MAT_DIRECTORY, f))
    category = mat["category"]
    subcategory = mat["labels"]

    assert all(subcategory[:, 0] == subcategory[0,0])

    category_index = category[0,0]
    subcategory_index = subcategory[0, 0]

    id = f[:-4]
    category = LABELS[id][0]
    subcategory = LABELS[id][1]

    if category in category_indexes:
        assert category_indexes[category] == category_index
    if subcategory in subcategory_indexes:
        assert subcategory_indexes[subcategory] == subcategory_index

    category_indexes[category] = category_index
    subcategory_indexes[subcategory] = subcategory_index


print(json.dumps({"categories": category_indexes, "subcategories": subcategory_indexes}))
