import os
import glob

# path = '/path/to/directory'
json_files = glob.glob('*.json')
# json_files = glob.glob(path + '/*.json')
for j in json_files:

    os.remove(j)
