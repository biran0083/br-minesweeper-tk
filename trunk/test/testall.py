#!/usr/bin/python
import os
test_list=[
"test1.py", "test2.py", "test3.py", "test4.py",
"test5.py",
]
for f in test_list:
	os.system("."+os.sep+f)
