"""
The NRRD integrity check performs the following verifications:
- Is it encoded as a NRRD file
- The header contains all the mandatory fields
- The 'space directions' header entry is conform to the 'sizes' header entry
- Number of element in the data array is conform to 'sizes' header entry
"""
import os
import time


#print("CHECK OS ENVIRON")
#print(os.environ['ACCESS_TOKEN'])
while True:
    time.sleep(4)
    print("CHECK OS GET")
    print(os.getenv('ACCESS_TOKEN', 'pas trouve'))

