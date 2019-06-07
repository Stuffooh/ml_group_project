import sys

usage = "filter-test-csv CSV-IN-FILE CSV-OUT-FILE"

if len(sys.argv) != 3:
    print(usage)
    exit(0)

csv_in = sys.argv[1]
csv_out = sys.argv[2]

with open(csv_in) as f:
    rows = f.read().split('\n')

with open(csv_out, 'w') as f:
    f.write('\n'.join((row for row in rows if "test" in row)))
