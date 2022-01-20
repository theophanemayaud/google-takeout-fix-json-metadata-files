# created by Théophane Mayaud for use when downloading large libraries
# from google photos, through / using Google Takeout (takeout.google.com)
# This is intended to work on macOS

# Use this freely, you can simply run it with :
#    - first argument: source directory where all archives were extracted.
#           should contain folders multiple folders with inside a Google Photos folder
#    - second argument: destination directory, where a
#           'Google Photos Takeout Merged' folder will be put, and all original files moved to it if no error.

import sys
import os
import numpy as np

# check input arguments (folder to scan)
numbArgs = len(sys.argv)
sourceDir = ""
destDir = ""
if numbArgs!=3:
    raise ValueError(\
        "\n\nError in input arguments:\n"\
        "    - first argument: source directory where all archives were extracted.\n"\
        "          should contain folders multiple folders with inside a Google Photos folder\n"\
        "   - second argument: destination directory, where a\n"\
        "         'Google Photos Takeout Merged' folder will be put,\n"\
        "          and all original files moved to it if no error. \n"\
        "          use this utility, you should use the syntax: \n" \
        "\nuse like this: 'python this-utility.py [source folder] [destination folder]'\n")
else:
    sourceDir = str(sys.argv[1])
    destDir = os.path.join(os.path.abspath(str(sys.argv[2])), "Google Photos Takeout Merged")
    
print(f"\nWill now move all from \n        {sourceDir}\n"\
      f"    to a single directory \n        {destDir}")


# scan files
files = []
for (dirpath, dirnames, filenames) in os.walk(sourceDir):
    for filename in filenames:
        filePathName = os.path.join(os.path.abspath(dirpath), filename)
        files.append(filePathName)
files = np.array(files)
print(f"\nFound {len(files)} files")

# Actually perform move:

nbUpdated = 0
nbErrors = 0
for filePathNameExt in files:
    if ".DS_Store" in filePathNameExt:
        continue
    
    if "/Google Photos/" in filePathNameExt:
        pathElements = filePathNameExt.split('/')
        pathAfterGPhotos = ""
        for pathElem in pathElements:
            if len(pathAfterGPhotos)>0:
                 pathAfterGPhotos = os.path.join(pathAfterGPhotos, pathElem)
#                pathAfterGPhotos = pathAfterGPhotos + "/" + pathElem
            elif pathElem=="Google Photos":
                pathAfterGPhotos = "/"
        destFile = destDir + pathAfterGPhotos

        # check if directory exists
        destFileFolder = destFile.rsplit('/',1)[0]
        if not os.path.exists(destFileFolder):
            os.makedirs(destFileFolder)
        if os.path.exists(destFile):
            nbErrors+=1
            print(f"    Error: file exists in destination !\n"\
                  f"        {str(filePathNameExt)}\n"\
                  f"        {str(destFile)}")
        else:
            try:
                nbUpdated+=1;
                os.rename(filePathNameExt, destFile)
            except:
                nbErrors+=1
                nbUpdated-=1;
                print(f"    Unknown error moving file from/to\n"\
                      f"        {str(filePathNameExt)}\n"\
                      f"        {str(destFile)}")

            
print(f"    Moved {nbUpdated} files")
print(f"    Got {nbErrors} errors")
